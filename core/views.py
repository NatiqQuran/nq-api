from django.http import HttpResponse
from rest_framework import viewsets, permissions
from .models import ErrorLog, Phrase, PhraseTranslation, Notification
from .serializers import (ErrorLogSerializer, PhraseModifySerializer,
                          PhraseSerializer,
                          PhraseTranslationSerializer,
                          NotificationSerializer)
from rest_framework.decorators import action
from storages.backends.s3boto3 import S3Boto3Storage
from rest_framework.response import Response
from django.conf import settings
from drf_spectacular.utils import extend_schema, OpenApiParameter, extend_schema_view, OpenApiExample, inline_serializer
from drf_spectacular.types import OpenApiTypes
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from core.pagination import CustomLimitOffsetPagination


@extend_schema_view(
    list=extend_schema(summary="List all error logs"),
    retrieve=extend_schema(summary="Retrieve a specific error log by ID"),
    create=extend_schema(summary="Create a new error log entry"),
    update=extend_schema(summary="Update an existing error log entry"),
    partial_update=extend_schema(summary="Partially update an error log entry"),
    destroy=extend_schema(summary="Delete an error log entry")
)
class ErrorLogViewSet(viewsets.ModelViewSet):
    queryset = ErrorLog.objects.all()
    serializer_class = ErrorLogSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]


@extend_schema_view(
    list=extend_schema(summary="List all phrases"),
    retrieve=extend_schema(summary="Retrieve a specific phrase by UUID"),
    create=extend_schema(summary="Create a new phrase"),
    update=extend_schema(summary="Update an existing phrase"),
    partial_update=extend_schema(summary="Partially update a phrase"),
    destroy=extend_schema(summary="Delete a phrase")
)
class PhraseViewSet(viewsets.ModelViewSet):
    queryset = Phrase.objects.all()
    serializer_class = PhraseSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly or permissions.DjangoModelPermissions]
    lookup_field = "uuid"
    # filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    # search_fields = ["recitation_date", "recitation_location", "recitation_type"]
    # ordering_fields = ['created_at', 'duration', 'recitation_date']
    # pegination_class = None

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='language',
                location=OpenApiParameter.QUERY,
                type=str,
                required=True,
                description="Language code for the translation (required)."
            ),
        ],
        summary="Modify phrase translations",
        description="Modify phrase translations for a given language. The 'language' query parameter is required."
    )
    @action(detail=False, methods=['post'], serializer_class=PhraseModifySerializer)
    def modify(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        language = self.request.query_params.get('language')
        phrases = serializer.data["phrases"]

        for p in phrases:
            val = phrases[p]
            phrase = Phrase.objects.filter(phrase=p).first()
            if phrase is None:
                return HttpResponse(content=f"Phrase '{p}' not found!", status=404)

            phrase.translations.update_or_create(language=language, defaults={
                    "text": val, "creator_id": self.request.user.id,
                    }
                )
        return HttpResponse(content="Done", status=200)

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


@extend_schema_view(
    list=extend_schema(summary="List all phrase translations"),
    retrieve=extend_schema(summary="Retrieve a specific phrase translation by ID"),
    create=extend_schema(summary="Create a new phrase translation"),
    update=extend_schema(summary="Update an existing phrase translation"),
    partial_update=extend_schema(summary="Partially update a phrase translation"),
    destroy=extend_schema(summary="Delete a phrase translation")
)
class PhraseTranslationViewSet(viewsets.ModelViewSet):
    queryset = PhraseTranslation.objects.all()
    serializer_class = PhraseTranslationSerializer
    permission_classes = [permissions.IsAuthenticated]


class Storage(S3Boto3Storage):
    """Storage object for s3
    
    Default location is uncategorized, and bucket name is
    from settings.

    Args:
        S3Boto3Storage (S3Boto3Storage): Storage
    """
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    default_acl = 'public-read'
    file_overwrite = False
    location = 'uncategorized'

@extend_schema_view(
    list=extend_schema(summary="List all notifications"),
    retrieve=extend_schema(summary="Retrieve a specific notification by UUID"),
    create=extend_schema(summary="Create a new notification"),
    update=extend_schema(summary="Update an existing notification"),
    partial_update=extend_schema(summary="Partially update a notification"),
    destroy=extend_schema(summary="Delete a notification")
)
class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [DjangoModelPermissions]
    pagination_class = CustomLimitOffsetPagination

    def get_permissions(self):
        if self.action == 'me':
            return [IsAuthenticated()]
        return [DjangoModelPermissions()]

    @extend_schema(
        summary="Get the current user's notifications (paginated)",
        description="Returns a paginated list of the current user's notifications. Marks notifications in the current page as 'got_notification' if not already marked.",
        responses={200: NotificationSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def me(self, request):
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
        paginator = CustomLimitOffsetPagination()
        page = paginator.paginate_queryset(notifications, request)
        # Update status to 'got_notification' only for notifications in the current page
        to_update = []
        for n in page:
            if n.status == Notification.STATUS_NOTHING:
                n.status = Notification.STATUS_GOT
                to_update.append(n)
        if to_update:
            Notification.objects.bulk_update(to_update, ['status'])
        serializer = self.get_serializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @extend_schema(
        summary="Mark notifications as viewed",
        description="Marks all notifications with status 'got_notification' as 'viewed_notification' for the current user.",
        responses={200: OpenApiTypes.OBJECT}
    )
    @action(detail=False, methods=['get'])
    def viewed(self, request):
        notifications = Notification.objects.filter(user=request.user, status=Notification.STATUS_GOT)
        updated_count = notifications.update(status=Notification.STATUS_VIEWED)
        return Response({'detail': 'Notifications marked as viewed.', 'updated': updated_count})

    @extend_schema(
        summary="Mark a notification as opened",
        description="Marks a specific notification as 'opened_notification' using its uuid (provided as a query parameter).",
        parameters=[
            OpenApiParameter(
                name='uuid',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=True,
                description="UUID of the notification to mark as opened."
            )
        ],
        responses={200: OpenApiTypes.OBJECT, 400: OpenApiTypes.OBJECT, 404: OpenApiTypes.OBJECT}
    )
    @action(detail=False, methods=['get'])
    def opened(self, request):
        uuid = request.query_params.get('uuid')
        if not uuid:
            return Response({'detail': 'Notification uuid is required.'}, status=400)
        try:
            notification = Notification.objects.get(user=request.user, uuid=uuid)
        except Notification.DoesNotExist:
            return Response({'detail': 'Notification not found.'}, status=404)
        notification.status = Notification.STATUS_OPENED
        notification.save(update_fields=['status'])
        return Response({'detail': 'Notification marked as opened.'})
