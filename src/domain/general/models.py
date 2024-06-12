from typing import Generic, TypeVar

T = TypeVar("T")


class PaginatedResponse(Generic[T]):

    def __init__(self, page: int, per_page: int, pages_count: int, total: int, data: list[T]):
        self._page = page
        self._per_page = per_page
        self._pages_count = pages_count
        self._total = total
        self._data = data

    def get_page(self) -> int:
        return self._page

    def get_per_page(self) -> int:
        return self._per_page

    def get_pages_count(self) -> int:
        return self._pages_count

    def get_total(self) -> int:
        return self._total

    def get_data(self) -> list[T]:
        return self._data
