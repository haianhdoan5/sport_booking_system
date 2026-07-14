from django.contrib import admin

from .models import Booking, Field

admin.site.site_header = "SportBooking Administration"
admin.site.site_title = "SportBooking Admin"
admin.site.index_title = "Quản lý sân và đơn đặt"


@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    list_display = ("name", "field_type", "price_per_hour", "is_active")
    list_filter = ("field_type", "is_active")
    search_fields = ("name",)
    list_editable = ("is_active",)
    ordering = ("name",)
    list_per_page = 20


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "field",
        "user",
        "start_time",
        "end_time",
        "status",
        "total_price",
        "created_at",
    )
    list_filter = ("status", "field", "created_at")
    search_fields = ("user__username", "field__name")
    date_hierarchy = "created_at"
    readonly_fields = ("total_price", "created_at")
    ordering = ("-created_at",)
    list_per_page = 20
