from rest_framework import pagination
from rest_framework.response import Response


class CustomPagination(pagination.PageNumberPagination):
    page_size = 100
    page_size_query_param = "size"
    max_page_size = 100
    page_query_param = "page"

    def get_paginated_response(self, data):
        custom_page_size = self.request.query_params.get(self.page_size_query_param, None)
        if custom_page_size:
            custom_page_size = int(custom_page_size)
        return Response(
            {
                "page_size": custom_page_size or self.page_size,
                "total_objects": self.page.paginator.count,
                "total_pages": self.page.paginator.num_pages,
                "current_page_number": self.page.number,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
                "count": 0,
            }
        )
