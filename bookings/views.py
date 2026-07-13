from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render

from .forms import BookingForm
from .models import Booking, Field


# Trang chủ hiển thị danh sách các sân thể thao
def home_view(request):
    # Lấy tất cả các sân có trạng thái đang hoạt động
    active_fields = Field.objects.filter(is_active=True)
    return render(request, "bookings/field_list.html", {"fields": active_fields})


# View để xử lý việc đặt sân
@login_required  # Đăng nhập mới được đặt sân
def book_field_view(request, field_id):
    # Lấy thông tin cái sân mà khách vừa bấm vào
    field = get_object_or_404(Field, id=field_id)

    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            # Tạo đơn đặt nhưng chưa lưu vội vào Database (commit=False)
            booking = form.save(commit=False)
            booking.user = request.user  # Gán người đặt là người đang đăng nhập
            booking.field = field  # Gán sân được đặt

            try:
                booking.save()
                messages.success(
                    request, f"Chúc mừng! Bạn đã đặt {field.name} thành công."
                )
                return redirect("home")  # Đặt xong quay về trang chủ
            except ValidationError as e:
                # Nếu bị lỗi (trùng lịch, sai giờ), bắt lỗi và báo ra màn hình
                messages.error(request, e.message)
    else:
        form = BookingForm()

    return render(request, "bookings/booking_form.html", {"field": field, "form": form})


# View để xử lý việc đăng ký tài khoản người dùng
def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Lưu user mới vào Database
            login(request, user)  # Đăng nhập luôn cho user sau khi tạo thành công
            messages.success(
                request, f"Chào mừng {user.username}! Bạn đã đăng ký thành công."
            )
            return redirect("home")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    else:
        form = UserCreationForm()

    return render(request, "bookings/register.html", {"form": form})


@login_required
def booking_history_view(request):
    # Lấy danh sách đơn đặt user
    user_bookings = Booking.objects.filter(user=request.user).order_by("-created_at")

    return render(request, "bookings/booking_history.html", {"bookings": user_bookings})


@login_required
def cancel_booking_view(request, booking_id):
    # Lấy đúng đơn đặt sân dựa trên ID và bắt buộc phải là đơn của người đang đăng nhập
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    # Chỉ cho phép hủy nếu đơn đang ở trạng thái PENDING
    if booking.status == "PENDING":
        booking.status = "CANCELLED"
        booking.save()
        messages.success(
            request, f"Đã hủy thành công đơn đặt sân {booking.field.name}."
        )
    else:
        messages.error(
            request,
            "Bạn không thể hủy đơn này vì nó đã được xác nhận hoặc đã hủy từ trước.",
        )

    return redirect("booking_history")
