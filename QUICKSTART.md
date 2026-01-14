# Quick Start Guide

Hướng dẫn nhanh để chạy Package Search & Report Tool

## Bước 1: Cài đặt Dependencies

### Option A: Sử dụng py312 environment (Khuyên dùng)

```bash
# Activate environment
conda activate py312

# Cài đặt dependencies
cd report_tools
pip install -r requirements.txt
```

### Option B: Tạo environment mới

```bash
# Tạo environment mới
conda create -n package_tool python=3.12 -y

# Activate
conda activate package_tool

# Cài đặt
cd report_tools
pip install -r requirements.txt
```

## Bước 2: Kiểm tra cài đặt

```bash
# Run test script
python test_modules.py
```

Nếu thấy "✅ All tests passed successfully!" là OK!

## Bước 3: Chạy Web UI

```bash
streamlit run app.py
```

App sẽ tự động mở browser tại: http://localhost:8501

## Bước 4: Sử dụng

### Tìm kiếm gói cước

**Option 1: Tìm kiếm cụ thể**
1. Nhập mã gói vào ô search (vd: D15, BIG, GAME)
2. Click "🔍 Tìm kiếm"
3. Xem kết quả

**Option 2: Xem toàn bộ**
1. Click "📋 Show All" để xem tất cả gói
2. Sử dụng phân trang để điều hướng (tự động bật với >50 gói)
3. Hoặc dùng filters trước khi Show All để thu hẹp kết quả

### Export kết quả

1. Sau khi có kết quả search
2. Chọn view mode: Bảng hoặc Thẻ chi tiết
3. Click nút Export:
   - **📊 Export to Excel**: Xuất ra file .xlsx với formatting đẹp
   - **📄 Export to CSV**: Xuất ra file .csv đơn giản
   - **📋 Export Summary**: Xuất ra file tổng hợp thống kê

### Sử dụng Filters (Sidebar)

- **Nguồn**: Lọc theo myvnpt, vinaphone, digishop
- **Khoảng giá**: Slider để chọn range giá
- **Dung lượng**: Slider để chọn range data (GB)
- **Độ chính xác**: Điều chỉnh độ chính xác fuzzy search (50-100%)

## Features chính

✅ **Fuzzy Search**: Tìm gần đúng (D15 → D150, D15V, etc.)  
✅ **Fast**: Search trong 17K+ packages < 100ms  
✅ **Export**: Excel, CSV, Summary reports  
✅ **Filters**: Lọc theo source, price, data  
✅ **Responsive UI**: Giao diện thân thiện, dễ dùng  

## Troubleshooting

### Lỗi: "ModuleNotFoundError: No module named 'pandas'"

```bash
# Install dependencies
pip install -r requirements.txt
```

### Lỗi: "FileNotFoundError: unified_packages_clean.csv"

Đảm bảo file CSV nằm trong thư mục `report_tools/`

### Streamlit không mở browser

Truy cập thủ công: http://localhost:8501

### Port 8501 đã được sử dụng

```bash
# Dùng port khác
streamlit run app.py --server.port 8502
```

## Ví dụ queries

- `D15` - Tìm gói D15 và các biến thể
- `BIG` - Tìm tất cả gói BIG
- `game` - Tìm gói game
- `6000` - Tìm gói giá 6000đ
- `ST` - Tìm gói bắt đầu với ST

## Keyboard Shortcuts trong Streamlit

- `R` - Reload app
- `Ctrl+Shift+P` - Command palette

## Liên hệ & Báo lỗi

Nếu gặp vấn đề, hãy:
1. Check file log trong terminal
2. Kiểm tra lại dependencies đã install đủ chưa
3. Thử reload browser (Ctrl+R)
