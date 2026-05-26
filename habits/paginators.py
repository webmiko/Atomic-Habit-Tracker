"""Пагинация списков привычек."""

from rest_framework.pagination import PageNumberPagination


class HabitPageNumberPagination(PageNumberPagination):
    """Постраничный вывод привычек по пять записей на страницу."""

    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 5
