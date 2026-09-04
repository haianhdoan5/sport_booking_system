from datetime import date, datetime, time, timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import BookingForm, RegistrationForm
from .models import Booking, Field


SCHEDULE_START_HOUR = 7
SCHEDULE_END_HOUR = 22


def _selected_booking_date(request):
    raw_date = request.POST.get("selected_date") or request.GET.get("date")

    if not raw_date and request.method == "POST":
        raw_date = request.POST.get("start_time", "")[:10]

    try:
        selected_date = date.fromisoformat(raw_date) if raw_date else timezone.localdate()
    except ValueError:
        selected_date = timezone.localdate()

    return max(selected_date, timezone.localdate())


def _daily_availability(field, selected_date):
    current_timezone = timezone.get_current_timezone()
    day_start = timezone.make_aware(datetime.combine(selected_date, time.min), current_timezone)
    day_end = day_start + timedelta(days=1)
    current_time = timezone.now()

    occupied_bookings = list(
        Booking.objects.filter(
            field=field,
            status__in=[Booking.Status.PENDING, Booking.Status.CONFIRMED],
            start_time__lt=day_end,
            end_time__gt=day_start,
        )
        .only("start_time", "end_time")
        .order_by("start_time")
    )

    slots = []

    for hour in range(SCHEDULE_START_HOUR, SCHEDULE_END_HOUR):
        slot_start = timezone.make_aware(datetime.combine(selected_date, time(hour=hour)), current_timezone)
        slot_end = slot_start + timedelta(hours=1)
        is_occupied = any(
            booking.start_time < slot_end and booking.end_time > slot_start for booking in occupied_bookings
        )
        is_past = slot_start < current_time

        if is_occupied:
            status = "booked"
        elif is_past:
            status = "past"
        else:
            status = "available"

        slots.append(
            {
                "start_label": timezone.localtime(slot_start).strftime("%H:%M"),
                "end_label": timezone.localtime(slot_end).strftime("%H:%M"),
                "start_value": timezone.localtime(slot_start).strftime("%Y-%m-%dT%H:%M"),
                "end_value": timezone.localtime(slot_end).strftime("%Y-%m-%dT%H:%M"),
                "status": status,
            }
        )

    return slots


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
    selected_date = _selected_booking_date(request)
    availability_slots = _daily_availability(field, selected_date)

    if request.method == "POST":
        booking_instance = Booking(user=request.user, field=field)
        form = BookingForm(request.POST, instance=booking_instance)

        if form.is_valid():
            try:
                with transaction.atomic():
                    locked_field = get_object_or_404(Field.objects.select_for_update(), id=field.id, is_active=True)

                    booking = form.save(commit=False)
                    booking.field = locked_field
                    booking.save()

            except ValidationError as error:
                for error_message in error.messages:
                    form.add_error(None, error_message)

            else:
                formatted_price = f"{booking.total_price:,.0f}".replace(",", ".")
                messages.success(
                    request,
                    f"Đặt sân thành công. Mã booking: {booking.booking_code} - Tổng tiền: {formatted_price} VNĐ.",
                )

                return redirect("booking_history")

    else:
        first_available_slot = next(
            (slot for slot in availability_slots if slot["status"] == "available"),
            None,
        )
        initial_data = {}

        if first_available_slot:
            initial_data = {
                "start_time": first_available_slot["start_value"],
                "end_time": first_available_slot["end_value"],
            }

        form = BookingForm(initial=initial_data)

    context = {
        "field": field,
        "form": form,
        "selected_date": selected_date,
        "today": timezone.localdate(),
        "availability_slots": availability_slots,
    }

    return render(request, "bookings/booking_form.html", context)


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
    selected_status = request.GET.get("status", "").strip().upper()
    valid_statuses = {value for value, _label in Booking.Status.choices}
    booking_queryset = Booking.objects.filter(user=request.user)

    summary = booking_queryset.aggregate(
        total=Count("id"),
        pending=Count("id", filter=Q(status=Booking.Status.PENDING)),
        confirmed=Count("id", filter=Q(status=Booking.Status.CONFIRMED)),
        completed=Count("id", filter=Q(status=Booking.Status.COMPLETED)),
        cancelled=Count("id", filter=Q(status=Booking.Status.CANCELLED)),
    )

    if selected_status in valid_statuses:
        booking_queryset = booking_queryset.filter(status=selected_status)
    else:
        selected_status = ""

    user_bookings = booking_queryset.select_related("field").order_by("-created_at")

    context = {
        "bookings": user_bookings,
        "booking_statuses": Booking.Status.choices,
        "selected_status": selected_status,
        "summary": summary,
    }

    return render(request, "bookings/booking_history.html", context)


@login_required
@require_POST
def cancel_booking_view(request, booking_id):
    booking = get_object_or_404(Booking.objects.select_related("field"), id=booking_id, user=request.user)

    updated_rows = Booking.objects.filter(id=booking.id, user=request.user, status=Booking.Status.PENDING).update(
        status=Booking.Status.CANCELLED
    )

    if updated_rows == 0:
        messages.error(request, f"Booking {booking.booking_code} không còn ở trạng thái chờ xác nhận nên không thể hủy.")
    else:
        messages.success(request, f"Đã hủy booking {booking.booking_code} tại {booking.field.name}.")

    return redirect("booking_history")


@staff_member_required
def admin_dashboard_view(request):
    today = timezone.localdate()
    current_timezone = timezone.get_current_timezone()
    day_start = timezone.make_aware(datetime.combine(today, time.min), current_timezone)
    day_end = day_start + timedelta(days=1)
    active_booking_statuses = [Booking.Status.PENDING, Booking.Status.CONFIRMED]
    completed_revenue = (
        Booking.objects.filter(status=Booking.Status.COMPLETED).aggregate(total=Sum("total_price"))["total"]
        or Decimal("0")
    )
    status_counts = {
        item["status"]: item["total"]
        for item in Booking.objects.values("status").annotate(total=Count("id"))
    }
    status_cards = [
        {"value": value, "label": label, "count": status_counts.get(value, 0)}
        for value, label in Booking.Status.choices
    ]
    upcoming_bookings = (
        Booking.objects.filter(status__in=active_booking_statuses, start_time__gte=timezone.now())
        .select_related("field", "user")
        .order_by("start_time")[:8]
    )
    popular_fields = (
        Field.objects.annotate(
            booking_count=Count(
                "bookings",
                filter=Q(
                    bookings__status__in=[
                        Booking.Status.PENDING,
                        Booking.Status.CONFIRMED,
                        Booking.Status.COMPLETED,
                    ]
                ),
            )
        )
        .filter(booking_count__gt=0)
        .order_by("-booking_count", "name")[:5]
    )

    context = {
        "today": today,
        "total_fields": Field.objects.count(),
        "active_fields": Field.objects.filter(is_active=True).count(),
        "total_bookings": Booking.objects.count(),
        "today_bookings": Booking.objects.filter(start_time__gte=day_start, start_time__lt=day_end)
        .exclude(status=Booking.Status.CANCELLED)
        .count(),
        "pending_bookings": status_counts.get(Booking.Status.PENDING, 0),
        "completed_revenue": completed_revenue,
        "status_cards": status_cards,
        "upcoming_bookings": upcoming_bookings,
        "popular_fields": popular_fields,
    }

    return render(request, "bookings/admin_dashboard.html", context)
