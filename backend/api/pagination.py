from rest_framework.pagination import PageNumberPagination

from constants import (
    PAGES_PAGINATION_PAGE_SIZE,
    PAGES_PAGINATION_PAGE_SIZE_QUERY_PARAM
)


class PagesPagination(PageNumberPagination):
    page_size_query_param = PAGES_PAGINATION_PAGE_SIZE_QUERY_PARAM
    page_size = PAGES_PAGINATION_PAGE_SIZE
