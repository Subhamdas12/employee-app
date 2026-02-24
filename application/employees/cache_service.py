from django.core.cache import cache

from .repository import fetch_employee_page


PAGE_SIZE = 1000
EMPLOYEE_PAGE_CACHE_KEY_PREFIX = "employees:page"
EMPLOYEE_CACHED_PAGES_KEY = "employees:cached_pages"
CACHE_SOURCE_DB = "postgresql"
CACHE_SOURCE_REDIS = "redis"


def _employee_page_cache_key(page: int) -> str:
    return f"{EMPLOYEE_PAGE_CACHE_KEY_PREFIX}:{int(page)}"


def _mark_page_as_cached(page: int) -> None:
    cached_pages = cache.get(EMPLOYEE_CACHED_PAGES_KEY) or []
    page_set = set(cached_pages)
    page_set.add(int(page))
    cache.set(EMPLOYEE_CACHED_PAGES_KEY, sorted(page_set))


def get_employees_for_display(page: int, page_size: int = PAGE_SIZE) -> tuple[list[dict], str]:
    cache_key = _employee_page_cache_key(page)
    cached_payload = cache.get(cache_key)
    if cached_payload is not None:
        return cached_payload, CACHE_SOURCE_REDIS

    employee_data = fetch_employee_page(page, page_size)
    cache.set(cache_key, employee_data)
    _mark_page_as_cached(page)
    return employee_data, CACHE_SOURCE_DB


def cache_page_if_missing(page: int, employee_data: list[dict]) -> bool:
    cache_key = _employee_page_cache_key(page)
    inserted = cache.add(cache_key, employee_data)
    _mark_page_as_cached(page)
    return bool(inserted)


def clear_employee_page_cache() -> None:
    cached_pages = cache.get(EMPLOYEE_CACHED_PAGES_KEY) or []
    keys = [_employee_page_cache_key(page) for page in cached_pages]
    if keys:
        cache.delete_many(keys)
    cache.delete(EMPLOYEE_CACHED_PAGES_KEY)


def has_cached_page(page: int) -> bool:
    cache_key = _employee_page_cache_key(page)
    return cache.get(cache_key) is not None


def get_cached_page(page: int) -> list[dict] | None:
    return cache.get(_employee_page_cache_key(page))
