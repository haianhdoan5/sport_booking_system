from django.contrib import admin

from .models import Booking, Field

# Đăng ký các bảng của bạn vào trang Admin
admin.site.register(Field)
admin.site.register(Booking)
