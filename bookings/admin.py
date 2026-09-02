from django.contrib import admin
from django.utils.html import format_html

from .models import Booking, Field, Payment, Review

# =========================================================
# CẤU HÌNH TRANG ADMIN
# =========================================================

admin.site.site_header = "SportBooking Administration"
admin.site.site_title = "SportBooking Admin"
admin.site.index_title = "Quản lý hệ thống đặt sân thể thao"


# =========================================================
# FIELD ADMIN
# =========================================================


@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    list_display = ("name", "field_type", "formatted_price", "activity_status", "created_at")

    list_filter = ("field_type", "is_active")

    search_fields = ("name", "address")

    ordering = ("field_type", "name")

    list_per_page = 20

    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Thông tin sân", {"fields": ("name", "field_type", "description", "address", "price_per_hour", "image")}),
        ("Trạng thái hoạt động", {"fields": ("is_active",)}),
        ("Thông tin hệ thống", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    @admin.display(description="Giá mỗi giờ", ordering="price_per_hour")
    def formatted_price(self, obj):
        price = f"{obj.price_per_hour:,.0f}".replace(",", ".")
        return f"{price} VNĐ"

    @admin.display(description="Trạng thái", boolean=False, ordering="is_active")
    def activity_status(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="'
                "background:#d1fae5;"
                "color:#065f46;"
                "padding:5px 10px;"
                "border-radius:999px;"
                'font-weight:700;">'
                "{}"
                "</span>",
                "Đang mở",
            )

        return format_html(
            '<span style="'
            "background:#fee2e2;"
            "color:#991b1b;"
            "padding:5px 10px;"
            "border-radius:999px;"
            'font-weight:700;">'
            "{}"
            "</span>",
            "Tạm ngưng",
        )


# =========================================================
# BOOKING ADMIN
# =========================================================


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "booking_code",
        "field",
        "user",
        "start_time",
        "end_time",
        "formatted_total_price",
        "colored_status",
        "created_at",
    )

    list_filter = ("status", "field__field_type", "field", "start_time", "created_at")

    search_fields = ("booking_code", "user__username", "field__name")

    autocomplete_fields = ("user", "field")

    readonly_fields = ("booking_code", "total_price", "created_at", "updated_at")

    ordering = ("-created_at",)

    list_per_page = 25

    list_select_related = ("field", "user")

    actions = ("confirm_selected_bookings", "complete_selected_bookings", "cancel_selected_bookings")

    fieldsets = (
        ("Thông tin đơn đặt", {"fields": ("booking_code", "user", "field")}),
        ("Thời gian đặt sân", {"fields": ("start_time", "end_time")}),
        ("Thanh toán và trạng thái", {"fields": ("total_price", "status")}),
        ("Thông tin bổ sung", {"fields": ("note",)}),
        ("Thông tin hệ thống", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    @admin.display(description="Tổng tiền", ordering="total_price")
    def formatted_total_price(self, obj):
        if obj.total_price is None:
            return "—"

        price = f"{obj.total_price:,.0f}".replace(",", ".")
        return f"{price} VNĐ"

    @admin.display(description="Trạng thái", ordering="status")
    def colored_status(self, obj):
        status_styles = {
            Booking.Status.PENDING: ("#fef3c7", "#92400e"),
            Booking.Status.CONFIRMED: ("#d1fae5", "#065f46"),
            Booking.Status.COMPLETED: ("#dbeafe", "#1e40af"),
            Booking.Status.CANCELLED: ("#fee2e2", "#991b1b"),
        }

        background, color = status_styles.get(obj.status, ("#e5e7eb", "#374151"))

        return format_html(
            '<span style="'
            "background:{};"
            "color:{};"
            "padding:5px 10px;"
            "border-radius:999px;"
            'font-weight:700;">'
            "{}"
            "</span>",
            background,
            color,
            obj.get_status_display(),
        )

    @admin.action(description="Xác nhận các đơn đã chọn")
    def confirm_selected_bookings(self, request, queryset):
        updated_rows = queryset.filter(status=Booking.Status.PENDING).update(status=Booking.Status.CONFIRMED)

        self.message_user(request, f"Đã xác nhận {updated_rows} đơn đặt sân.")

    @admin.action(description="Đánh dấu các đơn đã hoàn thành")
    def complete_selected_bookings(self, request, queryset):
        updated_rows = queryset.filter(status=Booking.Status.CONFIRMED).update(status=Booking.Status.COMPLETED)

        self.message_user(request, f"Đã hoàn thành {updated_rows} đơn đặt sân.")

    @admin.action(description="Hủy các đơn đã chọn")
    def cancel_selected_bookings(self, request, queryset):
        updated_rows = queryset.exclude(status__in=[Booking.Status.CANCELLED, Booking.Status.COMPLETED]).update(
            status=Booking.Status.CANCELLED
        )

        self.message_user(request, f"Đã hủy {updated_rows} đơn đặt sân.")


# =========================================================
# PAYMENT ADMIN
# =========================================================


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("booking", "formatted_amount", "method", "colored_payment_status", "transaction_code", "paid_at")

    list_filter = ("method", "status", "created_at")

    search_fields = ("booking__booking_code", "booking__user__username", "transaction_code")

    autocomplete_fields = ("booking",)

    readonly_fields = ("amount", "created_at", "updated_at")

    ordering = ("-created_at",)

    list_per_page = 25

    list_select_related = ("booking", "booking__user")

    fieldsets = (
        ("Thông tin thanh toán", {"fields": ("booking", "amount", "method", "status")}),
        ("Thông tin giao dịch", {"fields": ("transaction_code", "paid_at")}),
        ("Thông tin hệ thống", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    @admin.display(description="Số tiền", ordering="amount")
    def formatted_amount(self, obj):
        if obj.amount is None:
            return "—"

        price = f"{obj.amount:,.0f}".replace(",", ".")
        return f"{price} VNĐ"

    @admin.display(description="Trạng thái", ordering="status")
    def colored_payment_status(self, obj):
        status_styles = {
            Payment.Status.PENDING: ("#fef3c7", "#92400e"),
            Payment.Status.PAID: ("#d1fae5", "#065f46"),
            Payment.Status.FAILED: ("#fee2e2", "#991b1b"),
        }

        background, color = status_styles.get(obj.status, ("#e5e7eb", "#374151"))

        return format_html(
            '<span style="'
            "background:{};"
            "color:{};"
            "padding:5px 10px;"
            "border-radius:999px;"
            'font-weight:700;">'
            "{}"
            "</span>",
            background,
            color,
            obj.get_status_display(),
        )


# =========================================================
# REVIEW ADMIN
# =========================================================


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("user", "field", "rating_display", "booking", "created_at")

    list_filter = ("rating", "field", "created_at")

    search_fields = ("user__username", "field__name", "booking__booking_code", "comment")

    autocomplete_fields = ("user", "field", "booking")

    readonly_fields = ("created_at", "updated_at")

    ordering = ("-created_at",)

    list_per_page = 25

    list_select_related = ("user", "field", "booking")

    fieldsets = (
        ("Thông tin đánh giá", {"fields": ("booking", "user", "field", "rating", "comment")}),
        ("Thông tin hệ thống", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    @admin.display(description="Đánh giá", ordering="rating")
    def rating_display(self, obj):
        stars = "★" * obj.rating
        empty_stars = "☆" * (5 - obj.rating)

        return format_html(
            '<span style="' "color:#f59e0b;" "font-size:16px;" 'font-weight:700;">' "{}{}" "</span>", stars, empty_stars
        )
