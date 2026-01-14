# Export Behavior Documentation

## 📥 Cách Export hoạt động

### ⚠️ Quan trọng: Export TOÀN BỘ Results

**Export luôn xuất TOÀN BỘ kết quả**, không chỉ trang đang hiển thị!

---

## 🎯 Use Cases & Behavior

### Case 1: Export sau Search
```
Action: Search "D15" → Tìm được 8 gói
Display: Hiển thị cả 8 gói (không cần pagination)
Export: Xuất CẢ 8 gói
```

### Case 2: Export sau Show All
```
Action: Click "Show All" → Load 17,286 gói
Display: Trang 1 hiển thị 1-50 (của 17,286)
Export: Xuất CẢ 17,286 gói (không chỉ 50 gói trang 1)
```

### Case 3: Export sau Show All + Filter
```
Action: 
  - Sidebar: Chọn source = "vinaphone"
  - Click "Show All" → Load 8,935 gói VinaPhone
Display: Trang 1 hiển thị 1-50 (của 8,935)
Export: Xuất CẢ 8,935 gói VinaPhone
```

### Case 4: Export khi đang ở trang 5
```
Action: 
  - Show All → 17,286 gói
  - Navigate đến trang 5
  - Click Export
Display: Trang 5 hiển thị 201-250
Export: Xuất CẢ 17,286 gói (không chỉ 201-250)
```

---

## 🖥️ UI Messages

### Before Export (Info)
Khi có pagination enabled, hiển thị:
```
ℹ️ Export sẽ xuất toàn bộ 17,286 gói (không chỉ trang hiện tại)
```

### After Export (Success)
```
✅ File Excel đã sẵn sàng! (17,286 gói)
✅ File CSV đã sẵn sàng! (17,286 gói)
✅ File Summary đã sẵn sàng! (17,286 gói)
```

---

## 🔍 Technical Details

### Code Logic
```python
# Display uses paginated_results
display_df = pd.DataFrame(paginated_results)  # Only current page

# Export uses full results
generator.generate_excel(results, ...)  # ALL results
generator.generate_csv(results, ...)    # ALL results
```

### Variables
- `results`: Full results list (all matches)
- `paginated_results`: Current page only (subset)
- `page_size`: Items per page (50/100/200/500)
- `current_page`: Current page number

---

## 📊 Export Performance

| Dataset Size | Export Format | Time |
|-------------|---------------|------|
| 100 gói | Excel | ~0.5s |
| 1,000 gói | Excel | ~1s |
| 10,000 gói | Excel | ~5s |
| 17,286 gói | Excel | ~8s |
| 100 gói | CSV | <0.1s |
| 17,286 gói | CSV | ~0.3s |

---

## 💡 Best Practices

### ✅ Recommended Workflow
1. **Lọc trước**: Dùng filters để thu hẹp results
2. **Verify**: Browse qua một vài trang để check data
3. **Export**: Export toàn bộ filtered results
4. **Confirm**: Check success message số gói

### ⚠️ Large Dataset Warning
Khi export >1000 gói:
- Excel export có thể mất 5-10 giây
- CSV export nhanh hơn (~1s)
- Browser có thể "not responding" tạm thời
- **Đừng close tab** khi đang export

---

## 🎨 UI Flow Diagram

```
User Action                    Display             Export
───────────────────────────────────────────────────────────
Click "Show All"       →       Page 1 (1-50)      
Navigate to Page 5     →       Page 5 (201-250)   
Click "Export Excel"   →       Still Page 5       → Export ALL 17K
Download file          →       ✅ 17,286 gói      
```

---

## 🧪 Testing Scenarios

### Test 1: Show All + Export
```
1. Click "Show All"
2. Wait for load (should show "Tìm thấy 17,286 gói")
3. Check pagination shows "Trang 1/346"
4. Click "Export to Excel"
5. ✅ Should see "Export sẽ xuất toàn bộ 17,286 gói"
6. Download and open file
7. ✅ File should contain 17,286 rows (+ header)
```

### Test 2: Filter + Show All + Export
```
1. Sidebar: Select source "myvnpt"
2. Click "Show All"
3. Should show "Tìm thấy 236 gói"
4. Click "Export to CSV"
5. ✅ Should see "Export sẽ xuất toàn bộ 236 gói"
6. Download and check
7. ✅ File should contain exactly 236 rows
```

### Test 3: Navigate + Export
```
1. Show All (17K gói)
2. Navigate to page 10
3. Verify showing items 451-500
4. Click "Export to Excel"
5. ✅ Export message should say "17,286 gói" NOT "50 gói"
6. ✅ File should have all 17,286 gói
```

---

## ❓ FAQ

### Q: Tại sao export không chỉ xuất trang hiện tại?
**A:** Để user có thể:
- Export toàn bộ catalog một lần
- Browse trước, export sau
- Không cần click export ở mỗi trang

### Q: Làm sao để export chỉ 1 trang?
**A:** Hiện tại không support. Workaround:
1. Dùng filters để giảm results
2. Export filtered results
3. Hoặc copy-paste từ table view

### Q: Export lâu quá, có bị lỗi không?
**A:** Không, export dataset lớn cần thời gian:
- 17K gói Excel: ~8-10 giây
- Browser có thể "freeze" tạm thời
- Đợi cho đến khi thấy download button

### Q: Có giới hạn số gói export không?
**A:** Không có hard limit, nhưng:
- Excel có giới hạn 1,048,576 rows
- CSV không giới hạn
- Recommend dùng CSV cho >100K gói

---

## 🔧 For Developers

### Change Export Behavior
Nếu muốn export chỉ current page:
```python
# Change from:
generator.generate_excel(results, ...)

# To:
generator.generate_excel(paginated_results, ...)
```

### Add Export Options
Có thể thêm radio button:
```python
export_mode = st.radio(
    "Export mode:",
    ["Toàn bộ results", "Chỉ trang hiện tại"]
)

if export_mode == "Chỉ trang hiện tại":
    data_to_export = paginated_results
else:
    data_to_export = results
```

---

**Last Updated**: 2026-01-14  
**Current Behavior**: Export ALL results  
**Status**: Working as designed ✅
