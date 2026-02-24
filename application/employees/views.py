from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from .cache_service import PAGE_SIZE, get_employees_for_display
from .repository import fetch_employee_count


@login_required
def employee_list_view(request: HttpRequest) -> HttpResponse:
    page_param = request.GET.get("page", "1")
    try:
        page = int(page_param)
    except ValueError:
        page = 1

    page = max(page, 1)
    employees, source = get_employees_for_display(page=page, page_size=PAGE_SIZE)
    total_count = fetch_employee_count()
    range_start = ((page - 1) * PAGE_SIZE) + 1 if total_count > 0 else 0
    range_end = min(page * PAGE_SIZE, total_count) if total_count > 0 else 0
    has_prev = page > 1
    has_next = page * PAGE_SIZE < total_count

    context = {
        "employees": employees,
        "source": source,
        "count": total_count,
        "page": page,
        "page_size": PAGE_SIZE,
        "range_start": range_start,
        "range_end": range_end,
        "has_prev": has_prev,
        "has_next": has_next,
        "prev_page": page - 1,
        "next_page": page + 1,
    }
    return render(request, "employees/employee_list.html", context)


def signup_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("employee-list")

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("employee-list")
    else:
        form = UserCreationForm()

    return render(request, "employees/signup.html", {"form": form})


def login_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("employee-list")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            next_url = request.POST.get("next")
            if next_url:
                return redirect(next_url)
            return redirect("employee-list")
    else:
        form = AuthenticationForm()

    return render(request, "employees/login.html", {"form": form, "next": request.GET.get("next", "")})


def logout_view(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        logout(request)
    return redirect("login")
