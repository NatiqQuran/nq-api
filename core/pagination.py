from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response


class CustomLimitOffsetPagination(LimitOffsetPagination):
    """
    Custom pagination using Django REST Framework's LimitOffsetPagination.
    Uses 'limit' and 'offset' parameters for pagination.
    """
    default_limit = 200
    limit_query_param = 'limit'
    offset_query_param = 'offset'
    max_limit = 10000

    def get_paginated_response(self, data):
        """
        Return only the data without pagination metadata.
        """
        return Response(data)

    def get_paginated_response_schema(self, schema):
        return schema