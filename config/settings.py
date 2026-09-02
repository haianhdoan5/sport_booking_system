import os
from pathlib import Path

from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def env_bool(name, default=False):
    value = os.getenv(name)

    if value is None:
        return default

    return value.strip().lower() in {"1", "true", "yes", "on"}


# Khóa mặc định chỉ sử dụng để chạy local.
# Khi deploy, đặt biến môi trường DJANGO_SECRET_KEY.
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "django-insecure-development-only")

DEBUG = env_bool("DJANGO_DEBUG", True)

ALLOWED_HOSTS = [
    host.strip() for host in os.getenv("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",") if host.strip()
]


# Application definition

INSTALLED_APPS = [
    "jazzmin",
    "bookings.apps.BookingsConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DB_ENGINE = os.getenv("DB_ENGINE", "mysql").strip().lower()

if DB_ENGINE == "sqlite":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / os.getenv("DB_NAME", "db.sqlite3"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.getenv("DB_NAME", "sport_booking_db"),
            "USER": os.getenv("DB_USER", "root"),
            "PASSWORD": os.getenv("DB_PASSWORD", ""),
            "HOST": os.getenv("DB_HOST", "127.0.0.1"),
            "PORT": os.getenv("DB_PORT", "3306"),
            "OPTIONS": {"charset": "utf8mb4"},
        }
    }


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = "vi"

TIME_ZONE = "Asia/Ho_Chi_Minh"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"

JAZZMIN_SETTINGS = {
    "site_title": "SportBooking Admin",
    "site_header": "SportBooking",
    "site_brand": "SportBooking",
    "welcome_sign": "Đăng nhập hệ thống quản lý SportBooking",
    "copyright": "SportBooking",
    "site_url": "/",
    # Thanh tìm kiếm chung
    "search_model": ["bookings.Booking", "bookings.Field", "auth.User"],
    # Menu phía trên
    "topmenu_links": [
        {"name": "Trang quản trị", "url": "admin:index"},
        {"name": "Xem website", "url": "home", "new_window": True},
        {"app": "bookings"},
    ],
    # Menu tài khoản phía trên bên phải
    "usermenu_links": [{"name": "Xem website", "url": "home", "new_window": True}],
    # Hiển thị menu trái
    "show_sidebar": True,
    # Tự động mở rộng menu
    "navigation_expanded": True,
    # Thứ tự menu
    "order_with_respect_to": ["bookings", "bookings.booking", "bookings.field", "auth", "auth.user", "auth.group"],
    # Biểu tượng cho ứng dụng và model
    "icons": {
        "bookings": "fas fa-calendar-check",
        "bookings.booking": "fas fa-calendar-alt",
        "bookings.field": "fas fa-table-tennis-paddle-ball",
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.group": "fas fa-users",
    },
    "default_icon_parents": "fas fa-folder",
    "default_icon_children": "fas fa-circle",
    # Hiện modal thay vì cửa sổ popup cũ
    "related_modal_active": True,
    # Giao diện form
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "bookings.booking": "collapsible",
        "bookings.field": "horizontal_tabs",
        "auth.user": "collapsible",
        "auth.group": "vertical_tabs",
    },
    # Mở trình chỉnh giao diện trực tiếp
    "show_ui_builder": True,
    # Chưa dùng CSS admin cũ
    "custom_css": None,
    "custom_js": None,
    "language_chooser": False,
}

JAZZMIN_UI_TWEAKS = {
    # Giao diện sáng
    "theme": "flatly",
    # Navbar sáng
    "navbar": "navbar-white navbar-light",
    # Màu nhấn
    "accent": "accent-primary",
    # Cố định navbar và sidebar
    "navbar_fixed": True,
    "sidebar_fixed": True,
    # Không đóng khung toàn bộ nội dung
    "layout_boxed": False,
    # Sidebar tối giống ảnh mẫu
    "sidebar": "sidebar-dark-primary",
    # Cách hiển thị menu con
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    # Màu các nút
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success",
    },
}
