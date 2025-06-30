from django.contrib.auth.models import Group, User
from django.contrib.auth import login
from rest_framework import permissions, viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny 
from rest_framework.response import Response
from knox.models import AuthToken
from knox.views import LoginView as KnoxLoginView
from .serializers import ProfileSerializer, UserSerializer, GroupSerializer, LoginSerializer
from rest_framework.authtoken.serializers import AuthTokenSerializer
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample

class LoginView(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    @extend_schema(
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(
                response=None,
                description="Login successful, returns auth token."
            ),
            400: OpenApiResponse(description="Invalid credentials.")
        },
        description="Login with username and password. Returns Knox token.",
        examples=[
            OpenApiExample(
                'Login Example',
                value={"username": "testuser", "password": "yourpassword"},
                request_only=True
            )
        ]
    )
    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return super(LoginView, self).post(request, format=None)

class AuthViewSet(viewsets.GenericViewSet):
    """
    Authentication ViewSet for user registration.
    
    * /auth/register/ - Register a new user
    """
    permission_classes = [AllowAny]
    serializer_class = UserSerializer
    
    def get_queryset(self):
        return User.objects.all()  # Required for DRF to show in the API root

    @extend_schema(
        request=UserSerializer,
        responses={
            201: OpenApiResponse(
                response=None,
                description="User registered successfully, returns user data and token."
            ),
            400: OpenApiResponse(description="Validation error.")
        },
        description="Register a new user with username, password, and email.",
        examples=[
            OpenApiExample(
                'Register Example',
                value={
                    "username": "newuser",
                    "password": "yourpassword",
                    "password2": "yourpassword",
                    "email": "newuser@example.com",
                    "first_name": "New",
                    "last_name": "User"
                },
                request_only=True
            )
        ]
    )
    @action(methods=['post'], detail=False)
    def register(self, request):
        """
        Register a new user with username, password, and email.
        Returns user data and Knox token upon successful registration.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            _, token = AuthToken.objects.create(user)
            return Response({
                'user': UserSerializer(user).data,
                'token': token
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Optionally, subclass Knox's LogoutView to add schema info
from knox.views import LogoutView as KnoxLogoutView

class LogoutView(KnoxLogoutView):
    @extend_schema(
        responses={204: OpenApiResponse(description="Logout successful.")},
        description="Logout current user (invalidate token)."
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all().order_by('name')
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

# TODO: add remove account
class ProfileViewSet(viewsets.mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get', 'post'], serializer_class=ProfileSerializer)
    def me(self, request):
        if request.method == "GET":
            serializer = self.get_serializer(self.request.user)
            return Response(serializer.data)
        elif request.method == "POST":
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            username = serializer.data.get("username")
            first_name = serializer.data.get("first_name")
            last_name = serializer.data.get("last_name")
            user = self.request.user
            if username:
                user.username = username
            if first_name:
                user.first_name = first_name
            if last_name:
                user.last_name = last_name
            user.save()
            return Response(serializer.data,status=200)
