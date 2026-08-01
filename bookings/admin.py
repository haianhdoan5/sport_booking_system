from django.contrib import admin
from django.utils.html import format_html

from .models import Booking, Field

admin.site.site_header = "SportBooking Administration"
admin.site.site_title = "SportBooking Admin"
admin.site.index_title = "Quản lý sân và đơn đặt"


@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    list_display = ("name", "field_type", "formatted_price", "activity_status")

    list_filter = ("field_type", "is_active")

    search_fields = ("name",)

    list_editable = ()

    ordering = ("field_type", "name")

    list_per_page = 20

    fieldsets = (
        ("Thông tin sân", {"fields": ("name", "field_type", "price_per_hour")}),
        ("Trạng thái hoạt động", {"fields": ("is_active",)}),
    )

    @admin.display(description="Giá mỗi giờ", ordering="price_per_hour")
    def formatted_price(self, obj):
        price = f"{obj.price_per_hour:,.0f}".replace(",", ".")

        return f"{price} VNĐ"

    @admin.display(description="Trạng thái", ordering="is_active")
    def activity_status(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="'
                "background:#d1fae5;"
                "color:#065f46;"
                "padding:5px 10px;"
                "border-radius:999px;"
                'font-weight:700;">'
                "Đang mở"
                "</span>"
            )

        return format_html(
            '<span style="'
            "background:#fee2e2;"
            "color:#991b1b;"
            "padding:5px 10px;"
            "border-radius:999px;"
            'font-weight:700;">'
            "Tạm ngưng"
            "</span>"
        )


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "field",
        "user",
        "start_time",
        "end_time",
        "formatted_total_price",
        "colored_status",
        "created_at",
    )

    list_filter = ("status", "field__field_type", "field", "start_time", "created_at")

    search_fields = ("user__username", "field__name")

    autocomplete_fields = ("user", "field")

    readonly_fields = ("total_price", "created_at")

    date_hierarchy = "start_time"

    ordering = ("-created_at",)

    list_per_page = 25

    list_select_related = ("field", "user")

    actions = ("confirm_selected_bookings", "cancel_selected_bookings")

    fieldsets = (
        ("Thông tin khách hàng", {"fields": ("user", "field")}),
        ("Thời gian đặt sân", {"fields": ("start_time", "end_time")}),
        ("Thanh toán và trạng thái", {"fields": ("total_price", "status")}),
        ("Thông tin hệ thống", {"fields": ("created_at",), "classes": ("collapse",)}),
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

    @admin.action(description="Hủy các đơn đã chọn")
    def cancel_selected_bookings(self, request, queryset):
        updated_rows = queryset.exclude(status=Booking.Status.CANCELLED).update(status=Booking.Status.CANCELLED)

        self.message_user(request, f"Đã hủy {updated_rows} đơn đặt sân.")
