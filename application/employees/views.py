import json

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

from .cache_service import PAGE_SIZE, get_employees_for_display
from .repository import fetch_employee_count


def _parse_page_param(request: HttpRequest) -> int:
    page_param = request.GET.get("page", "1")
    try:
        page = int(page_param)
    except ValueError:
        page = 1
    return max(page, 1)


def _parse_request_data(request: HttpRequest) -> tuple[dict, JsonResponse | None]:
    if request.content_type and "application/json" in request.content_type.lower():
        try:
            payload = json.loads(request.body.decode("utf-8") or "{}")
        except (json.JSONDecodeError, UnicodeDecodeError):
            return {}, JsonResponse({"detail": "Invalid JSON payload."}, status=400)

        if not isinstance(payload, dict):
            return {}, JsonResponse({"detail": "JSON payload must be an object."}, status=400)

        return payload, None

    return request.POST.dict(), None


def _build_employee_pagination_context(page: int) -> dict:
    employees, source = get_employees_for_display(page=page, page_size=PAGE_SIZE)
    total_count = fetch_employee_count()
    range_start = ((page - 1) * PAGE_SIZE) + 1 if total_count > 0 else 0
    range_end = min(page * PAGE_SIZE, total_count) if total_count > 0 else 0
    has_prev = page > 1
    has_next = page * PAGE_SIZE < total_count

    return {
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


@login_required
def employee_list_view(request: HttpRequest) -> HttpResponse:
    page = _parse_page_param(request)
    context = _build_employee_pagination_context(page)
    return render(request, "employees/employee_list.html", context)


@login_required
def employee_list_api_view(request: HttpRequest) -> JsonResponse:
    page = _parse_page_param(request)
    payload = _build_employee_pagination_context(page)
    payload["results"] = payload.pop("employees")
    return JsonResponse(payload)


@csrf_exempt
def api_signup_view(request: HttpRequest) -> JsonResponse:
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed. Use POST."}, status=405)

    data, error_response = _parse_request_data(request)
    if error_response is not None:
        return error_response

    form = UserCreationForm(data)
    if not form.is_valid():
        return JsonResponse({"errors": form.errors}, status=400)

    user = form.save()
    login(request, user)
    return JsonResponse(
        {
            "message": "Signup successful.",
            "user": {"id": user.id, "username": user.username},
        },
        status=201,
    )


@csrf_exempt
def api_login_view(request: HttpRequest) -> JsonResponse:
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed. Use POST."}, status=405)

    data, error_response = _parse_request_data(request)
    if error_response is not None:
        return error_response

    form = AuthenticationForm(request, data=data)
    if not form.is_valid():
        return JsonResponse({"errors": form.errors}, status=400)

    user = form.get_user()
    login(request, user)
    return JsonResponse(
        {
            "message": "Login successful.",
            "user": {"id": user.id, "username": user.username},
        }
    )


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
