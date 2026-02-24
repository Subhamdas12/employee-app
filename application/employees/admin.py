from django.contrib import admin

from .models import Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "education",
        "joining_year",
        "city",
        "payment_tier",
        "age",
        "gender",
        "ever_benched",
        "experience_in_current_domain",
        "leave_or_not",
    )
    search_fields = ("education", "city", "gender", "ever_benched")
