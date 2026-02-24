from django.urls import path

from .views import employee_list_view, login_view, logout_view, signup_view


urlpatterns = [
    path("", employee_list_view, name="employee-list"),
    path("signup/", signup_view, name="signup"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
]
