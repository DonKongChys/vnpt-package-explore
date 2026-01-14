"""
Package Search & Report Tool - Streamlit Web UI
Main application entry point
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys
from datetime import datetime
from io import BytesIO

# Import our modules
from data_loader import PackageDataLoader
from search_engine import FuzzySearchEngine
from report_generator import ReportGenerator

# Page configuration
st.set_page_config(
    page_title="Package Search & Report Tool",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .stats-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .result-count {
        font-size: 1.2rem;
        font-weight: bold;
        color: #28a745;
        margin: 1rem 0;
    }
    .stDataFrame {
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    """Load and cache package data"""
    try:
        loader = PackageDataLoader("unified_packages_clean.csv")
        df = loader.load_data()
        stats = loader.get_statistics()
        return df, stats, loader
    except FileNotFoundError:
        st.error("❌ File unified_packages_clean.csv không tìm thấy!")
        st.stop()
    except Exception as e:
        st.error(f"❌ Lỗi khi load dữ liệu: {e}")
        st.stop()


@st.cache_resource
def create_search_engine(df):
    """Create and cache search engine"""
    return FuzzySearchEngine(df)


def format_currency(value):
    """Format value as Vietnamese currency"""
    if pd.isna(value) or value == '':
        return '-'
    try:
        return f"{float(value):,.0f} đ"
    except (ValueError, TypeError):
        return str(value)


def format_data_gb(value):
    """Format data volume"""
    if pd.isna(value) or value == '':
        return '-'
    try:
        return f"{float(value):.2f} GB"
    except (ValueError, TypeError):
        return str(value)


def format_cycle(value):
    """Format cycle days"""
    if pd.isna(value) or value == '':
        return '-'
    try:
        days = float(value)
        if days >= 30:
            months = days / 30
            return f"{months:.0f} tháng"
        elif days >= 7:
            weeks = days / 7
            return f"{weeks:.1f} tuần"
        else:
            return f"{days:.0f} ngày"
    except (ValueError, TypeError):
        return str(value)


def display_package_card(package, show_score=False):
    """Display package information in an expandable card"""
    score_text = f" (Score: {package.get('_similarity_score', 0):.1f}%)" if show_score else ""
    
    with st.expander(f"📦 **{package['package_code']}** - {package['package_name']}{score_text}"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Thông tin cơ bản**")
            st.write(f"🏷️ **Mã gói:** {package['package_code']}")
            st.write(f"📛 **Tên:** {package['package_name']}")
            st.write(f"💰 **Giá:** {format_currency(package.get('price'))}")
            st.write(f"📅 **Chu kỳ:** {format_cycle(package.get('cycle_days'))}")
            st.write(f"🌐 **Nguồn:** {package.get('source', '-')}")
        
        with col2:
            st.markdown("**Dung lượng**")
            st.write(f"📊 **Data:** {format_data_gb(package.get('data_gb'))}")
            st.write(f"📞 **Phút gọi:** {package.get('voice_minutes', '-')}")
            st.write(f"💬 **SMS:** {package.get('sms_count', '-')}")
            st.write(f"🔖 **Loại:** {package.get('package_type', '-')}")
        
        with col3:
            st.markdown("**Cú pháp**")
            st.write(f"✅ **ĐK:** {package.get('registration_syntax', '-')}")
            st.write(f"❌ **Hủy:** {package.get('cancellation_syntax', '-')}")
            st.write(f"🔍 **Tra cứu:** {package.get('check_syntax', '-')}")
            st.write(f"📞 **Hotline:** {package.get('support_hotline', '-')}")
        
        # Description
        if package.get('description'):
            st.markdown("**📝 Mô tả:**")
            st.info(package['description'])
        
        # Full description
        if package.get('full_description'):
            with st.expander("Xem chi tiết đầy đủ"):
                st.text(package['full_description'])
        
        # Additional info
        if package.get('eligibility'):
            st.markdown("**📋 Điều kiện:**")
            st.caption(package['eligibility'])
        
        if package.get('renewal_policy'):
            st.markdown("**🔄 Chính sách gia hạn:**")
            st.caption(package['renewal_policy'])
        
        if package.get('original_link'):
            st.markdown(f"**🔗 Link gốc:** [{package['original_link']}]({package['original_link']})")


def main():
    """Main application"""
    
    # Header
    st.markdown('<div class="main-header">📦 Package Search & Report Tool</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Load data
    with st.spinner("Đang tải dữ liệu..."):
        df, stats, loader = load_data()
        search_engine = create_search_engine(df)
    
    # Sidebar - Statistics and Filters
    with st.sidebar:
        st.header("📊 Thống kê")
        
        st.metric("Tổng số gói", f"{stats['total_packages']:,}")
        
        st.markdown("**Theo nguồn:**")
        for source, count in stats['sources'].items():
            st.write(f"• {source}: {count:,} gói")
        
        st.markdown("**Khoảng giá:**")
        st.write(f"• Min: {stats['price_stats']['min']:,.0f} đ")
        st.write(f"• Max: {stats['price_stats']['max']:,.0f} đ")
        st.write(f"• TB: {stats['price_stats']['mean']:,.0f} đ")
        
        st.markdown("**Dung lượng data:**")
        st.write(f"• Min: {stats['data_stats']['min_gb']:.2f} GB")
        st.write(f"• Max: {stats['data_stats']['max_gb']:.2f} GB")
        
        st.markdown("---")
        
        # Filters
        st.header("🔧 Bộ lọc")
        
        filter_source = st.multiselect(
            "Nguồn",
            options=list(stats['sources'].keys()),
            default=[]
        )
        
        price_range = st.slider(
            "Khoảng giá (VNĐ)",
            min_value=0,
            max_value=int(stats['price_stats']['max']),
            value=(0, int(stats['price_stats']['max'])),
            step=1000,
            format="%d đ"
        )
        
        data_range = st.slider(
            "Dung lượng (GB)",
            min_value=0.0,
            max_value=float(stats['data_stats']['max_gb']),
            value=(0.0, float(stats['data_stats']['max_gb'])),
            step=0.5,
            format="%.1f GB"
        )
        
        search_threshold = st.slider(
            "Độ chính xác tìm kiếm (%)",
            min_value=50,
            max_value=100,
            value=60,
            step=5,
            help="Độ tương đồng tối thiểu với từ khóa tìm kiếm"
        )
    
    # Main content area
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        search_query = st.text_input(
            "🔍 Tìm kiếm gói cước (mã gói hoặc tên)",
            placeholder="Ví dụ: D15, BIG, GAME... hoặc regex: ^D.*5$",
            help="Nhập mã gói hoặc tên gói để tìm kiếm. Hỗ trợ tìm gần đúng và regex."
        )
    
    with col2:
        search_mode = st.selectbox(
            "Chế độ tìm",
            options=["Fuzzy", "Regex"],
            help="Fuzzy: Tìm gần đúng | Regex: Tìm theo pattern"
        )
    
    with col3:
        top_n = st.number_input(
            "Số kết quả",
            min_value=5,
            max_value=100,
            value=20,
            step=5
        )
    
    # Search mode specific options
    if search_mode == "Regex":
        col_regex1, col_regex2 = st.columns(2)
        with col_regex1:
            regex_search_in = st.selectbox(
                "Tìm trong:",
                options=["Cả code & name", "Chỉ code", "Chỉ name", "Description", "Tất cả fields"],
                help="Chọn field để search regex"
            )
        with col_regex2:
            case_sensitive = st.checkbox("Case sensitive", value=False)
        
        # Map display to internal values
        regex_field_map = {
            "Cả code & name": "both",
            "Chỉ code": "code",
            "Chỉ name": "name",
            "Description": "description",
            "Tất cả fields": "all"
        }
        regex_field = regex_field_map[regex_search_in]
        
        # Show regex examples
        if search_query:
            st.caption("💡 Ví dụ regex: ^D.*$ (bắt đầu D) | .*15.* (chứa 15) | ^(BIG|SUPER).*")
    else:
        # Fuzzy search suggestions
        if search_query and len(search_query) >= 1:
            suggestions = search_engine.get_suggestions(search_query, limit=5)
            if suggestions:
                st.caption(f"💡 Gợi ý: {', '.join(suggestions[:5])}")
    
    # Initialize session state for results
    if 'search_results' not in st.session_state:
        st.session_state.search_results = []
    
    # Search button
    col_btn1, col_btn2, col_btn3, col_btn4 = st.columns([1, 1, 1, 3])
    
    with col_btn1:
        search_button = st.button("🔍 Tìm kiếm", type="primary", use_container_width=True)
    
    with col_btn2:
        show_all_button = st.button("📋 Show All", use_container_width=True)
    
    with col_btn3:
        clear_button = st.button("🗑️ Xóa", use_container_width=True)
    
    if clear_button:
        st.session_state.search_results = []
        st.rerun()
    
    # Show all data
    if show_all_button:
        with st.spinner("Đang tải toàn bộ dữ liệu..."):
            # Get all packages and apply filters if any
            all_packages = df.to_dict('records')
            
            # Apply filters
            filtered_packages = all_packages.copy()
            
            if filter_source:
                filtered_packages = [p for p in filtered_packages if p.get('source') in filter_source]
            
            if price_range != (0, int(stats['price_stats']['max'])):
                min_p, max_p = price_range
                filtered_packages = [p for p in filtered_packages 
                                   if pd.notna(p.get('price')) and min_p <= p.get('price') <= max_p]
            
            if data_range != (0.0, float(stats['data_stats']['max_gb'])):
                min_d, max_d = data_range
                filtered_packages = [p for p in filtered_packages 
                                   if pd.notna(p.get('data_gb')) and min_d <= p.get('data_gb') <= max_d]
            
            # Reset page to 1 when showing all
            st.session_state.current_page = 1
            st.session_state.search_results = filtered_packages
            
            # Show info message
            if len(filtered_packages) > 1000:
                st.info(f"ℹ️ Đang hiển thị {len(filtered_packages):,} gói. Sử dụng phân trang để dễ dàng điều hướng.")
            
            st.rerun()
    
    # Perform search
    if search_button or search_query:
        if search_query and search_query.strip():
            with st.spinner("Đang tìm kiếm..."):
                # Choose search method based on mode
                if search_mode == "Regex":
                    try:
                        # Regex search
                        results = search_engine.search_regex(
                            pattern=search_query,
                            search_in=regex_field,
                            case_sensitive=case_sensitive,
                            top_n=top_n
                        )
                        
                        # Apply filters to regex results
                        if filter_source:
                            results = [r for r in results if r.get('source') in filter_source]
                        
                        if price_range != (0, int(stats['price_stats']['max'])):
                            min_p, max_p = price_range
                            results = [r for r in results 
                                     if pd.notna(r.get('price')) and min_p <= r.get('price') <= max_p]
                        
                        if data_range != (0.0, float(stats['data_stats']['max_gb'])):
                            min_d, max_d = data_range
                            results = [r for r in results 
                                     if pd.notna(r.get('data_gb')) and min_d <= r.get('data_gb') <= max_d]
                        
                        if not results:
                            st.warning("⚠️ Regex không match với gói nào. Kiểm tra lại pattern.")
                    except Exception as e:
                        st.error(f"❌ Lỗi regex: {e}")
                        results = []
                else:
                    # Fuzzy search
                    if filter_source or price_range != (0, int(stats['price_stats']['max'])) or \
                       data_range != (0.0, float(stats['data_stats']['max_gb'])):
                        
                        results = search_engine.search_with_filters(
                            query=search_query,
                            source=filter_source[0] if len(filter_source) == 1 else None,
                            min_price=price_range[0] if price_range[0] > 0 else None,
                            max_price=price_range[1] if price_range[1] < stats['price_stats']['max'] else None,
                            min_data=data_range[0] if data_range[0] > 0 else None,
                            max_data=data_range[1] if data_range[1] < stats['data_stats']['max_gb'] else None,
                            threshold=search_threshold,
                            top_n=top_n
                        )
                    else:
                        results = search_engine.search(
                            query=search_query,
                            top_n=top_n,
                            threshold=search_threshold
                        )
                    
                    # Apply source filter if multiple sources selected
                    if len(filter_source) > 1:
                        results = [r for r in results if r.get('source') in filter_source]
                
                st.session_state.search_results = results
    
    # Display results
    results = st.session_state.search_results
    
    if results:
        st.markdown(f'<div class="result-count">✅ Tìm thấy {len(results)} gói</div>', unsafe_allow_html=True)
        
        # View mode and pagination settings
        col_view1, col_view2, col_view3 = st.columns([2, 2, 2])
        
        with col_view1:
            view_mode = st.radio(
                "Chế độ hiển thị:",
                options=["📋 Bảng", "📇 Thẻ chi tiết"],
                horizontal=True
            )
        
        with col_view2:
            # Pagination for large datasets
            if len(results) > 50:
                use_pagination = st.checkbox("Sử dụng phân trang", value=True)
            else:
                use_pagination = False
        
        with col_view3:
            if use_pagination:
                page_size = st.selectbox(
                    "Số gói/trang:",
                    options=[50, 100, 200, 500],
                    index=0
                )
        
        # Pagination logic
        if use_pagination:
            total_pages = (len(results) - 1) // page_size + 1
            
            # Initialize page number in session state
            if 'current_page' not in st.session_state:
                st.session_state.current_page = 1
            
            # Page navigation
            col_nav1, col_nav2, col_nav3, col_nav4, col_nav5 = st.columns([1, 1, 2, 1, 1])
            
            with col_nav1:
                if st.button("⏮️ Đầu", disabled=(st.session_state.current_page == 1)):
                    st.session_state.current_page = 1
                    st.rerun()
            
            with col_nav2:
                if st.button("◀️ Trước", disabled=(st.session_state.current_page == 1)):
                    st.session_state.current_page -= 1
                    st.rerun()
            
            with col_nav3:
                st.markdown(f"<div style='text-align: center; padding: 0.5rem;'>Trang {st.session_state.current_page} / {total_pages}</div>", unsafe_allow_html=True)
            
            with col_nav4:
                if st.button("▶️ Sau", disabled=(st.session_state.current_page == total_pages)):
                    st.session_state.current_page += 1
                    st.rerun()
            
            with col_nav5:
                if st.button("⏭️ Cuối", disabled=(st.session_state.current_page == total_pages)):
                    st.session_state.current_page = total_pages
                    st.rerun()
            
            # Get current page results
            start_idx = (st.session_state.current_page - 1) * page_size
            end_idx = min(start_idx + page_size, len(results))
            paginated_results = results[start_idx:end_idx]
            
            st.caption(f"Hiển thị {start_idx + 1}-{end_idx} trong tổng số {len(results)} gói")
        else:
            paginated_results = results
        
        if view_mode == "📋 Bảng":
            # Table view
            display_df = pd.DataFrame(paginated_results)
            
            # Column selection options
            col_table_opt1, col_table_opt2 = st.columns([3, 1])
            
            with col_table_opt1:
                show_full_desc = st.checkbox("Hiển thị mô tả chi tiết", value=False, key="show_full_desc")
            
            with col_table_opt2:
                if show_full_desc:
                    max_desc_length = st.number_input(
                        "Độ dài mô tả (ký tự)",
                        min_value=50,
                        max_value=500,
                        value=200,
                        step=50,
                        key="max_desc_length"
                    )
            
            # Debug: Show available columns
            if show_full_desc:
                st.caption(f"📊 Debug: Columns available = {list(display_df.columns)}")
            
            # Select columns to display
            display_columns = [
                'package_code', 'package_name', 'source', 'price', 
                'cycle_days', 'data_gb', 'voice_minutes', 'description'
            ]
            
            # Add full description if requested
            if show_full_desc:
                # Ensure full_description exists in dataframe
                if 'full_description' not in display_df.columns:
                    st.warning("⚠️ Column 'full_description' không tồn tại trong data. Sử dụng 'description' thay thế.")
                    display_df['full_description'] = display_df['description'] if 'description' in display_df.columns else ''
                
                display_columns.append('full_description')
                st.caption(f"✅ Đã thêm cột 'full_description' vào display")
            
            # Add similarity score if available
            if '_similarity_score' in display_df.columns:
                display_columns.insert(0, '_similarity_score')
            
            # Filter existing columns
            display_columns = [col for col in display_columns if col in display_df.columns]
            
            # Format display
            display_df_formatted = display_df[display_columns].copy()
            
            # Rename columns
            column_names = {
                '_similarity_score': 'Score (%)',
                'package_code': 'Mã gói',
                'package_name': 'Tên',
                'source': 'Nguồn',
                'price': 'Giá (đ)',
                'cycle_days': 'Chu kỳ (ngày)',
                'data_gb': 'Data (GB)',
                'voice_minutes': 'Phút gọi',
                'description': 'Mô tả',
                'full_description': 'Mô tả chi tiết'
            }
            display_df_formatted.rename(columns=column_names, inplace=True)
            
            # Truncate full description if present
            if show_full_desc and 'Mô tả chi tiết' in display_df_formatted.columns:
                display_df_formatted['Mô tả chi tiết'] = display_df_formatted['Mô tả chi tiết'].apply(
                    lambda x: (str(x)[:max_desc_length] + '...') if pd.notna(x) and len(str(x)) > max_desc_length else str(x) if pd.notna(x) else '-'
                )
            
            # Format numbers
            if 'Giá (đ)' in display_df_formatted.columns:
                display_df_formatted['Giá (đ)'] = display_df_formatted['Giá (đ)'].apply(
                    lambda x: f"{x:,.0f}" if pd.notna(x) else '-'
                )
            
            # Adjust height based on whether full description is shown
            table_height = 600 if show_full_desc else 400
            
            # Configure column widths
            column_config = {}
            if 'Mô tả chi tiết' in display_df_formatted.columns:
                column_config['Mô tả chi tiết'] = st.column_config.TextColumn(
                    "Mô tả chi tiết",
                    width="large",
                    help="Click vào row để xem full text"
                )
            if 'Mô tả' in display_df_formatted.columns:
                column_config['Mô tả'] = st.column_config.TextColumn(
                    "Mô tả",
                    width="medium"
                )
            
            st.dataframe(
                display_df_formatted,
                use_container_width=True,
                hide_index=True,
                height=table_height,
                column_config=column_config
            )
            
            # Show expandable details below table
            if paginated_results:
                with st.expander("📖 Xem chi tiết gói đầu tiên"):
                    display_package_card(paginated_results[0], show_score=True)
        
        else:
            # Card view
            for pkg in paginated_results:
                display_package_card(pkg, show_score=True)
        
        # Export section
        st.markdown("---")
        st.subheader("📥 Xuất kết quả")
        
        # Show export info
        if use_pagination:
            st.info(f"ℹ️ Export sẽ xuất **toàn bộ {len(results):,} gói** (không chỉ trang hiện tại)")
        else:
            st.caption(f"Xuất {len(results):,} gói")
        
        col_export1, col_export2, col_export3 = st.columns(3)
        
        with col_export1:
            if st.button("📊 Export to Excel", use_container_width=True):
                try:
                    generator = ReportGenerator()
                    
                    # Generate in memory
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"package_report_{timestamp}.xlsx"
                    
                    # Generate Excel file
                    temp_path = Path(filename)
                    generator.generate_excel(results, str(temp_path), include_similarity=True)
                    
                    # Read file for download
                    with open(temp_path, 'rb') as f:
                        excel_data = f.read()
                    
                    st.download_button(
                        label="💾 Tải xuống Excel",
                        data=excel_data,
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    
                    # Clean up
                    temp_path.unlink()
                    
                    st.success(f"✅ File Excel đã sẵn sàng! ({len(results):,} gói)")
                    
                except Exception as e:
                    st.error(f"❌ Lỗi khi tạo Excel: {e}")
        
        with col_export2:
            if st.button("📄 Export to CSV", use_container_width=True):
                try:
                    generator = ReportGenerator()
                    
                    # Generate CSV in memory
                    df_export = pd.DataFrame(results)
                    csv_data = df_export.to_csv(index=False, encoding='utf-8-sig')
                    
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"package_report_{timestamp}.csv"
                    
                    st.download_button(
                        label="💾 Tải xuống CSV",
                        data=csv_data.encode('utf-8-sig'),
                        file_name=filename,
                        mime="text/csv"
                    )
                    
                    st.success(f"✅ File CSV đã sẵn sàng! ({len(results):,} gói)")
                    
                except Exception as e:
                    st.error(f"❌ Lỗi khi tạo CSV: {e}")
        
        with col_export3:
            if st.button("📋 Export Summary", use_container_width=True):
                try:
                    generator = ReportGenerator()
                    
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"package_summary_{timestamp}.txt"
                    
                    # Generate summary
                    temp_path = Path(filename)
                    generator.generate_summary_report(results, str(temp_path))
                    
                    with open(temp_path, 'r', encoding='utf-8') as f:
                        summary_data = f.read()
                    
                    st.download_button(
                        label="💾 Tải xuống Summary",
                        data=summary_data,
                        file_name=filename,
                        mime="text/plain"
                    )
                    
                    # Clean up
                    temp_path.unlink()
                    
                    st.success(f"✅ File Summary đã sẵn sàng! ({len(results):,} gói)")
                    
                except Exception as e:
                    st.error(f"❌ Lỗi khi tạo Summary: {e}")
    
    elif search_query and search_query.strip():
        st.warning("⚠️ Không tìm thấy kết quả phù hợp. Hãy thử:")
        st.info("• Giảm độ chính xác tìm kiếm\n• Thử từ khóa khác\n• Kiểm tra chính tả")
    else:
        st.info("💡 Nhập mã gói hoặc tên gói để bắt đầu tìm kiếm, hoặc click **📋 Show All** để xem toàn bộ dữ liệu!")
        
        # Show some sample packages
        st.subheader("📌 Các tùy chọn")
        
        col_opt1, col_opt2 = st.columns(2)
        
        with col_opt1:
            st.markdown("**Tìm kiếm gói phổ biến:**")
            popular_codes = ['D15', 'BIG', 'ST30', 'D10FT', 'GAME10']
            
            col_samples = st.columns(len(popular_codes))
            for idx, code in enumerate(popular_codes):
                with col_samples[idx]:
                    if st.button(f"🔍 {code}", use_container_width=True, key=f"sample_{code}"):
                        st.session_state.search_query = code
                        st.rerun()
        
        with col_opt2:
            st.markdown("**Hoặc xem theo nguồn:**")
            col_sources = st.columns(3)
            
            sources = list(stats['sources'].keys())
            for idx, source in enumerate(sources[:3]):  # Show top 3 sources
                with col_sources[idx]:
                    if st.button(f"📱 {source.upper()}", use_container_width=True, key=f"source_{source}"):
                        # Apply source filter and show all
                        with st.spinner(f"Đang tải gói từ {source}..."):
                            filtered = [p for p in df.to_dict('records') if p.get('source') == source]
                            st.session_state.search_results = filtered
                            st.session_state.current_page = 1
                            st.rerun()
    
    # Footer
    st.markdown("---")
    st.caption("📦 Package Search & Report Tool | Powered by Streamlit & RapidFuzz")


if __name__ == "__main__":
    main()
