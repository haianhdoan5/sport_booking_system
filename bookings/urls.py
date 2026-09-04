from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views
from .forms import LoginForm

urlpatterns = [
    path("", views.home_view, name="home"),
    path("fields/<int:field_id>/", views.field_detail_view, name="field_detail"),
    path("book/<int:field_id>/", views.book_field_view, name="book_field"),
    path("register/", views.register_view, name="register"),
    path("login/", LoginView.as_view(template_name="bookings/login.html", authentication_form=LoginForm), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("history/", views.booking_history_view, name="booking_history"),
    path("cancel/<int:booking_id>/", views.cancel_booking_view, name="cancel_booking"),
    path("dashboard/", views.admin_dashboard_view, name="admin_dashboard"),
]
