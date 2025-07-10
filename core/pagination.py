from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class CustomPageNumberPagination(PageNumberPagination):
    page_size = 20  # Default page size
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response(data)

    @staticmethod
    def get_paginated_response_schema(schema):
        # Return the schema as-is, since the response is just the data list
        return schema