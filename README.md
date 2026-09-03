# SportBooking

Website đặt và quản lý sân thể thao trực tuyến bằng Django. Phạm vi đồ án tập trung vào hai loại sân:

- Sân cầu lông
- Sân pickleball

Mỗi bản ghi `Field` là một sân vật lý độc lập. Các booking ở trạng thái chờ xác nhận hoặc đã xác nhận không được chồng thời gian trên cùng một sân.

## Chức năng hiện có

- Đăng ký, đăng nhập và đăng xuất
- Tìm kiếm sân theo tên, địa chỉ hoặc mô tả
- Lọc sân cầu lông và pickleball
- Xem danh sách và thông tin chi tiết của sân đang hoạt động
- Đặt sân và tự động tính tổng tiền theo thời lượng
- Ngăn đặt sân trong quá khứ, khoảng giờ không hợp lệ và lịch bị trùng
- Xem lịch sử và hủy booking đang chờ xác nhận
- Quản lý sân, booking, thanh toán và đánh giá qua Django Admin

## Cài đặt

Yêu cầu Python 3.12+ và MySQL 8.x.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Tạo cơ sở dữ liệu MySQL tên `sport_booking_db`, cập nhật thông tin kết nối trong `.env`, sau đó chạy:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo --with-bookings
python manage.py runserver
```

Website: `http://127.0.0.1:8000/`  
Admin: `http://127.0.0.1:8000/admin/`

Tài khoản khách hàng được tạo bởi lệnh seed:

```text
Tên đăng nhập: demo
Mật khẩu: Demo@12345
```

## Chạy nhanh bằng SQLite

Để kiểm tra project mà không cần khởi động MySQL, đặt các biến sau trong `.env`:

```env
DB_ENGINE=sqlite
DB_NAME=db.sqlite3
```

Sau đó chạy lại các lệnh `migrate`, `seed_demo` và `runserver` như trên.

## Kiểm tra project

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

## Quy trình Git

Các thay đổi đang được phát triển trên nhánh `develop`. Nhánh `main` chỉ nhận phiên bản ổn định cuối cùng của đồ án.
