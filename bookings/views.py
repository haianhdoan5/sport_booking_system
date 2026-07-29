from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import BookingForm, RegistrationForm
from .models import Booking, Field


def home_view(request):
    active_fields = Field.objects.filter(is_active=True).order_by("field_type", "name")

    return render(
        request,
        "bookings/field_list.html",
        {"fields": active_fields},
    )


@login_required
def book_field_view(request, field_id):
    field = get_object_or_404(
        Field,
        id=field_id,
        is_active=True,
    )

    if request.method == "POST":
        form = BookingForm(request.POST)

        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.field = field

            try:
                booking.save()

            except ValidationError as error:
                for message in error.messages:
                    form.add_error(None, message)

            else:
                messages.success(
                    request,
                    f"Bạn đã đặt {field.name} thành công.",
                )
                return redirect("home")
    else:
        form = BookingForm()

    return render(
        request,
        "bookings/booking_form.html",
        {
            "field": field,
            "form": form,
        },
    )


def register_view(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)

            messages.success(
                request,
                f"Chào mừng {user.username}! " "Bạn đã đăng ký thành công.",
            )

            return redirect("home")
    else:
        form = RegistrationForm()

    return render(
        request,
        "bookings/register.html",
        {"form": form},
    )


@login_required
def booking_history_view(request):
    user_bookings = (
        Booking.objects.filter(user=request.user)
        .select_related("field")
        .order_by("-created_at")
    )

    return render(
        request,
        "bookings/booking_history.html",
        {"bookings": user_bookings},
    )


@login_required
@require_POST
def cancel_booking_view(request, booking_id):
    booking = get_object_or_404(
        Booking,
        id=booking_id,
        user=request.user,
    )

    if booking.status != Booking.Status.PENDING:
        messages.error(
            request,
            "Đơn đã được xác nhận hoặc đã hủy trước đó.",
        )

        return redirect("booking_history")

    Booking.objects.filter(id=booking.id).update(status=Booking.Status.CANCELLED)

    messages.success(
        request,
        f"Đã hủy đơn đặt sân {booking.field.name}.",
    )

    return redirect("booking_history")
