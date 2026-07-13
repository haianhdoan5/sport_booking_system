from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from bookings.views import (
    book_field_view,
    booking_history_view,
    cancel_booking_view,
    home_view,
    register_view,
)

urlpatterns = [
    # Đường dẫn đến trang Admin
    path("admin/", admin.site.urls),
    path("", home_view, name="home"),
    path("book/<int:field_id>/", book_field_view, name="book_field"),
    # Quản lý tài khoản:
    path("register/", register_view, name="register"),
    path(
        "login/", LoginView.as_view(template_name="bookings/login.html"), name="login"
    ),
    path("logout/", LogoutView.as_view(next_page="home"), name="logout"),
    path("history/", booking_history_view, name="booking_history"),
    path("cancel/<int:booking_id>/", cancel_booking_view, name="cancel_booking"),
]
