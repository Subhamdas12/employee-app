from django.urls import path

from .views import (
    api_login_view,
    api_signup_view,
    employee_list_api_view,
    employee_list_view,
    login_view,
    logout_view,
    signup_view,
)


urlpatterns = [
    path("", employee_list_view, name="employee-list"),
    path("api/employees/", employee_list_api_view, name="employee-list-api"),
    path("api/signup/", api_signup_view, name="api-signup"),
    path("api/login/", api_login_view, name="api-login"),
    path("signup/", signup_view, name="signup"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
]
