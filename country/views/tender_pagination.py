from rest_framework.pagination import PageNumberPagination


class TenderPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = "limit"
    max_page_size = 1000
