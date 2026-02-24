from typing import Any

from .models import Employee


def _serialize_employee(employee: Employee) -> dict[str, Any]:
    return {
        "id": employee.id,
        "education": employee.education,
        "joining_year": employee.joining_year,
        "city": employee.city,
        "payment_tier": employee.payment_tier,
        "age": employee.age,
        "gender": employee.gender,
        "ever_benched": employee.ever_benched,
        "experience_in_current_domain": employee.experience_in_current_domain,
        "leave_or_not": employee.leave_or_not,
    }


def fetch_all_employees() -> list[dict[str, Any]]:
    queryset = Employee.objects.all().order_by("id")
    return [_serialize_employee(emp) for emp in queryset]


def fetch_employee_page(page: int, page_size: int) -> list[dict[str, Any]]:
    safe_page = max(int(page), 1)
    safe_page_size = max(int(page_size), 1)
    offset = (safe_page - 1) * safe_page_size
    queryset = Employee.objects.all().order_by("id")[offset : offset + safe_page_size]
    return [_serialize_employee(emp) for emp in queryset]


def fetch_employee_count() -> int:
    return Employee.objects.count()


def fetch_employee_batch_after_id(last_id: int, batch_size: int) -> list[dict[str, Any]]:
    queryset = Employee.objects.filter(id__gt=last_id).order_by("id")[:batch_size]
    return [_serialize_employee(emp) for emp in queryset]
