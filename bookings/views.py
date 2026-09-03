from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import BookingForm, RegistrationForm
from .models import Booking, Field


def home_view(request):
    query = request.GET.get("q", "").strip()
    selected_type = request.GET.get("type", "").strip().upper()
    valid_field_types = {value for value, _label in Field.Type.choices}

    active_fields = Field.objects.filter(is_active=True)
    total_active_fields = active_fields.count()

    if query:
        active_fields = active_fields.filter(
            Q(name__icontains=query) | Q(address__icontains=query) | Q(description__icontains=query)
        )

    if selected_type in valid_field_types:
        active_fields = active_fields.filter(field_type=selected_type)
    else:
        selected_type = ""

    active_fields = active_fields.order_by("field_type", "name")

    context = {
        "fields": active_fields,
        "field_types": Field.Type.choices,
        "query": query,
        "selected_type": selected_type,
        "total_active_fields": total_active_fields,
    }

    return render(request, "bookings/field_list.html", context)


def field_detail_view(request, field_id):
    field = get_object_or_404(Field, id=field_id, is_active=True)

    return render(request, "bookings/field_detail.html", {"field": field})


@login_required
def book_field_view(request, field_id):
    field = get_object_or_404(Field, id=field_id, is_active=True)

    if request.method == "POST":
        form = BookingForm(request.POST)

        if form.is_valid():
            try:
                with transaction.atomic():
                    locked_field = get_object_or_404(Field.objects.select_for_update(), id=field.id, is_active=True)

                    booking = form.save(commit=False)
                    booking.user = request.user
                    booking.field = locked_field
                    booking.save()

            except ValidationError as error:
                for error_message in error.messages:
                    form.add_error(None, error_message)

            else:
                messages.success(request, f"Bạn đã đặt {field.name} thành công.")

                return redirect("home")

    else:
        form = BookingForm()

    return render(request, "bookings/booking_form.html", {"field": field, "form": form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()

            login(request, user)

            messages.success(request, (f"Chào mừng {user.username}! " "Bạn đã đăng ký thành công."))

            return redirect("home")

    else:
        form = RegistrationForm()

    return render(request, "bookings/register.html", {"form": form})


@login_required
def booking_history_view(request):
    user_bookings = Booking.objects.filter(user=request.user).select_related("field").order_by("-created_at")

    return render(request, "bookings/booking_history.html", {"bookings": user_bookings})


@login_required
@require_POST
def cancel_booking_view(request, booking_id):
    booking = get_object_or_404(Booking.objects.select_related("field"), id=booking_id, user=request.user)

    updated_rows = Booking.objects.filter(id=booking.id, user=request.user, status=Booking.Status.PENDING).update(
        status=Booking.Status.CANCELLED
    )

    if updated_rows == 0:
        messages.error(request, "Đơn đã được xác nhận hoặc đã hủy trước đó.")
    else:
        messages.success(request, f"Đã hủy đơn đặt sân {booking.field.name}.")

    return redirect("booking_history")
