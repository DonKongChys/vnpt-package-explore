# Debug Guide: Full Description Column

## 🔍 Debugging Steps

### Step 1: Verify CSV has full_description column

```bash
cd report_tools
head -1 unified_packages_clean.csv | tr ',' '\n' | grep -n full_description
```

**Expected Output**:
```
11:full_description
```

✅ Column exists at position 11

---

### Step 2: Check data loaded correctly

```bash
python test_full_desc.py
```

**Expected Output**:
```
✅ Column 'full_description' exists
✅ Packages with full_description: 17,286 / 17,286
```

---

### Step 3: Run Streamlit and check UI

```bash
streamlit run app.py
```

**What to check**:

1. **Search or Show All** to get results
2. **Select "📋 Bảng" view mode**
3. **Check the checkbox**: ☑️ "Hiển thị mô tả chi tiết"
4. **Look for debug messages**:
   - `📊 Debug: Columns available = [...]`
   - `✅ Đã thêm cột 'full_description' vào display`
5. **Check table columns** - should see "Mô tả chi tiết" column

---

## 🐛 Common Issues & Solutions

### Issue 1: Column not appearing

**Symptoms**: Checkbox checked but no "Mô tả chi tiết" column

**Debug**:
- Look for debug message: `📊 Debug: Columns available = [...]`
- Check if 'full_description' is in the list

**Solution**:
- If NOT in list → Data loading issue
- If IN list → Display filtering issue

---

### Issue 2: Warning appears

**Warning**: `⚠️ Column 'full_description' không tồn tại trong data`

**This means**:
- Data was loaded but full_description column missing
- Fallback: Using 'description' instead

**Solution**:
1. Check CSV file integrity
2. Reload page (Ctrl+R)
3. Restart Streamlit

---

### Issue 3: Column appears but empty

**Symptoms**: "Mô tả chi tiết" column exists but shows `-` or empty

**Possible causes**:
- Data actually empty in CSV
- Truncation set too low
- Display formatting issue

**Debug**:
```python
# Check sample data
python test_full_desc.py
```

---

## 📋 Current Implementation

### Code Location: app.py Line ~486-526

```python
# 1. Checkbox to enable
show_full_desc = st.checkbox("Hiển thị mô tả chi tiết", ...)

# 2. Debug message
if show_full_desc:
    st.caption(f"📊 Debug: Columns available = {list(display_df.columns)}")

# 3. Add column
if show_full_desc:
    if 'full_description' not in display_df.columns:
        st.warning("⚠️ Column không tồn tại...")
        display_df['full_description'] = display_df['description']
    
    display_columns.append('full_description')
    st.caption(f"✅ Đã thêm cột...")

# 4. Column config
column_config = {
    'Mô tả chi tiết': st.column_config.TextColumn(
        "Mô tả chi tiết",
        width="large",
        help="Click vào row để xem full text"
    )
}
```

---

## ✅ Expected Behavior

### With Checkbox UNCHECKED (default)

```
Table Columns:
┌─────────┬──────┬────────┬───────┬─────┬──────┬─────────┐
│ Mã gói  │ Tên  │ Nguồn  │ Giá   │ ... │ Mô tả         │
└─────────┴──────┴────────┴───────┴─────┴──────┴─────────┘
```

### With Checkbox CHECKED

```
Debug Messages:
📊 Debug: Columns available = ['source', 'package_code', ..., 'full_description', ...]
✅ Đã thêm cột 'full_description' vào display

Table Columns:
┌─────────┬──────┬────────┬───────┬─────┬──────┬───────────────────┐
│ Mã gói  │ Tên  │ Nguồn  │ Giá   │ ... │ Mô tả│ Mô tả chi tiết   │
└─────────┴──────┴────────┴───────┴─────┴──────┴───────────────────┘
                                                 ↑ NEW COLUMN (large)
```

---

## 🧪 Manual Test Checklist

- [ ] 1. Start: `streamlit run app.py`
- [ ] 2. Click "📋 Show All" or search something
- [ ] 3. Verify results appear
- [ ] 4. Select "📋 Bảng" view mode
- [ ] 5. Check checkbox "Hiển thị mô tả chi tiết"
- [ ] 6. See debug message: `📊 Debug: Columns available = [...]`
- [ ] 7. Verify 'full_description' in the list
- [ ] 8. See success message: `✅ Đã thêm cột...`
- [ ] 9. Look at table headers - find "Mô tả chi tiết"
- [ ] 10. Verify column has content (not all `-`)
- [ ] 11. Adjust "Độ dài mô tả" slider
- [ ] 12. Verify truncation works (text + "...")

---

## 📸 Screenshot Verification Points

When checkbox is checked, you should see:

1. **Above table**:
   ```
   📊 Debug: Columns available = ['source', 'package_code', 'package_name', 
                                  'price', 'cycle_days', 'data_gb', 
                                  'voice_minutes', 'sms_count', 'package_type', 
                                  'description', 'full_description', ...]
   ✅ Đã thêm cột 'full_description' vào display
   ```

2. **In table header** (rightmost):
   ```
   ... | Phút gọi | Mô tả | Mô tả chi tiết |
   ```

3. **In table cells** (rightmost):
   ```
   ... | 100 | 5GB Data | Ưu đãi: - 5GB Data sử dụng trong 24h giờ... |
   ```

---

## 🆘 Still Not Working?

### Quick Fixes:

1. **Clear browser cache**: Ctrl+Shift+R
2. **Restart Streamlit**: Ctrl+C, then `streamlit run app.py`
3. **Check terminal** for error messages
4. **Take screenshot** of the debug messages
5. **Share** the debug output from console

### Get Debug Info:

```bash
# In terminal, run:
cd report_tools
python test_full_desc.py > debug_output.txt 2>&1

# Then check:
cat debug_output.txt
```

---

## 📞 Contact

If still not working after all steps:
1. Run `test_full_desc.py` and save output
2. Take screenshot of Streamlit UI with checkbox checked
3. Check if debug messages appear
4. Share the debug info

---

**Last Updated**: 2026-01-14
**Debug Mode**: Enabled in app.py
