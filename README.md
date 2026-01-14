# Package Search & Report Tool

Tool tìm kiếm và tạo báo cáo cho các gói cước viễn thông từ nhiều nguồn (MyVNPT, VinaPhone, DigiShop).

## Tính năng chính

- 🔍 **Fuzzy Search**: Tìm kiếm gói cước theo mã, hỗ trợ tìm gần đúng
- 📋 **Show All**: Xem toàn bộ 17K+ gói với pagination
- 📊 **Hiển thị chi tiết**: Xem đầy đủ thông tin 18 trường dữ liệu
- 📥 **Export**: Xuất **toàn bộ** kết quả ra Excel/CSV (không chỉ trang hiện tại)
- 📈 **Thống kê**: Dashboard thống kê theo nguồn, giá, loại gói

## Cài đặt

### 1. Activate Python 3.12 environment

```bash
conda activate py312
# hoặc
source venv/bin/activate
```

### 2. Install dependencies

```bash
cd report_tools
pip install -r requirements.txt
```

## Sử dụng

### Chạy Web UI

```bash
streamlit run app.py
```

App sẽ mở tại: http://localhost:8501

### Cách sử dụng

1. **Tìm kiếm gói**: Nhập mã gói (vd: D15, BIG, GAME) vào ô search
2. **Xem toàn bộ**: Click nút "📋 Show All" để xem tất cả gói (có phân trang)
3. **Xem kết quả**: Kết quả hiển thị dạng bảng hoặc thẻ chi tiết
4. **Phân trang**: Với dataset lớn, sử dụng nút điều hướng trang
5. **Mở rộng chi tiết**: Click vào card để xem mô tả chi tiết
6. **Export dữ liệu**: Click nút "Export to Excel" hoặc "Export to CSV"

### Ví dụ sử dụng

**Tìm kiếm cụ thể:**
- `D15` → Tìm các gói D15, D150, D15V, v.v.
- `BIG` → Tìm tất cả gói BIG
- `game` → Tìm gói GAME10, GAME, v.v.
- `6000` → Tìm gói có giá 6000đ

**Xem toàn bộ data:**
- Click "📋 Show All" → Hiển thị tất cả 17K+ gói
- Sử dụng filters (sidebar) trước khi Show All để lọc data
- Phân trang tự động bật với dataset >50 gói

**Xem theo nguồn:**
- Click nút nguồn (MYVNPT, VINAPHONE, DIGISHOP) ở trang chủ
- Hoặc dùng filter "Nguồn" trong sidebar

**Export toàn bộ:**
```
1. Click "📋 Show All" (load 17K+ gói)
2. Browse kết quả (có pagination)
3. Click "📊 Export to Excel"
4. → File Excel chứa TOÀN BỘ 17K+ gói (không chỉ trang hiện tại)
```

**💡 Pro Tip:**
- Dùng filters trước khi Show All để thu hẹp kết quả
- Export luôn xuất toàn bộ results, không phụ thuộc trang đang xem
- Check message "Export sẽ xuất toàn bộ X gói" trước khi export

## Cấu trúc dữ liệu

CSV chứa 17,287 gói cước với 18 trường:

| Trường | Mô tả |
|--------|-------|
| source | Nguồn dữ liệu (myvnpt/vinaphone/digishop) |
| package_code | Mã gói cước |
| package_name | Tên gói |
| price | Giá (VNĐ) |
| cycle_days | Chu kỳ (ngày) |
| data_gb | Dung lượng data (GB) |
| voice_minutes | Phút gọi |
| sms_count | Số SMS |
| package_type | Loại gói |
| description | Mô tả ngắn |
| full_description | Mô tả chi tiết |
| registration_syntax | Cú pháp đăng ký |
| cancellation_syntax | Cú pháp hủy |
| check_syntax | Cú pháp tra cứu |
| eligibility | Điều kiện áp dụng |
| renewal_policy | Chính sách gia hạn |
| support_hotline | Hotline hỗ trợ |
| original_link | Link gốc |

## Cấu trúc Project

```
report_tools/
├── app.py                      # Streamlit web app (entry point)
├── data_loader.py              # Load và cache CSV data
├── search_engine.py            # Fuzzy search logic
├── report_generator.py         # Generate Excel/CSV reports
├── unified_packages_clean.csv  # Dữ liệu gói cước
├── requirements.txt            # Dependencies
└── README.md                   # File này
```

## Performance

- Load data: ~1-2 giây cho 17K records
- Search: ~100ms với fuzzy matching
- Export Excel: ~2-3 giây

## Troubleshooting

### Lỗi "ModuleNotFoundError"

Đảm bảo đã install dependencies:
```bash
pip install -r requirements.txt
```

### Lỗi "FileNotFoundError: unified_packages_clean.csv"

Đảm bảo file CSV nằm cùng thư mục với app.py

### Streamlit không mở browser tự động

Truy cập thủ công: http://localhost:8501

## Liên hệ

Để báo lỗi hoặc đề xuất tính năng, vui lòng tạo issue.
