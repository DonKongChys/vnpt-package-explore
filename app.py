"""
Package Search & Report Tool - Streamlit Web UI
Main application entry point

Features:
- Tab 1: Package Details (unified_packages_clean.csv)
  * 17,287+ packages with full information
  * Fuzzy search with adjustable threshold (50-100%)
  * Regex search with field selection
  * Filters: source, price range, data volume
  * Export: Excel, CSV, Summary reports
  
- Tab 2: All Codes (all_codes.csv)
  * 1,580+ package codes
  * Fuzzy search for similarity matching
  * Regex search for pattern matching
  * Adjustable similarity threshold
  * Export: CSV and text formats

Both tabs support:
- Smart pagination for large datasets
- Multiple view modes (table/cards/list)
- Session state management
- Cached data loading for performance
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
        loader = PackageDataLoader("full_packages_map.csv")
        df = loader.load_data()
        stats = loader.get_statistics()
        return df, stats, loader
    except FileNotFoundError:
        st.error("❌ File full_packages_map.csv không tìm thấy!")
        st.stop()
    except Exception as e:
        st.error(f"❌ Lỗi khi load dữ liệu: {e}")
        st.stop()


@st.cache_data
def load_all_codes():
    """Load and cache all codes data"""
    try:
        df = pd.read_csv("all_codes.csv")
        stats = {
            'total_codes': len(df),
            'unique_codes': df['package_code'].nunique()
        }
        return df, stats
    except FileNotFoundError:
        st.error("❌ File all_codes.csv không tìm thấy!")
        st.stop()
    except Exception as e:
        st.error(f"❌ Lỗi khi load dữ liệu all_codes: {e}")
        st.stop()


@st.cache_resource
def create_search_engine(df):
    """Create and cache search engine"""
    return FuzzySearchEngine(df)


@st.cache_resource
def create_codes_search_engine(_df_codes):
    """Create and cache search engine for all_codes"""
    return FuzzySearchEngine(_df_codes)


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
            st.markdown("**Dung lượng & Lợi ích**")
            st.write(f"📊 **Data:** {format_data_gb(package.get('data_gb'))}")
            st.write(f"⏱️ **Thời gian hiệu lực:** {format_cycle(package.get('duration'))}")
            if package.get('data_limit_behavior'):
                st.write(f"🔄 **Hết data:** {package.get('data_limit_behavior')}")
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
        
        # Benefits section
        has_benefits = False
        if package.get('benefit_free_internal_calls'):
            st.markdown("**📞 Gọi nội mạng miễn phí:**")
            st.caption(package['benefit_free_internal_calls'])
            has_benefits = True
        if package.get('benefit_free_external_calls'):
            st.markdown("**📱 Gọi ngoại mạng miễn phí:**")
            st.caption(package['benefit_free_external_calls'])
            has_benefits = True
        if package.get('benefit_free_sms'):
            st.markdown("**💬 SMS miễn phí:**")
            st.caption(package['benefit_free_sms'])
            has_benefits = True
        if package.get('benefit_free_social_media_data'):
            st.markdown("**📱 Data mạng xã hội miễn phí:**")
            st.caption(package['benefit_free_social_media_data'])
            has_benefits = True
        if package.get('benefit_free_tv'):
            st.markdown("**📺 TV miễn phí:**")
            st.caption(package['benefit_free_tv'])
            has_benefits = True
        if package.get('benefit_other_benefits'):
            st.markdown("**🎁 Lợi ích khác:**")
            st.caption(package['benefit_other_benefits'])
            has_benefits = True
        if package.get('benefits'):
            st.markdown("**✨ Lợi ích:**")
            st.info(package['benefits'])
            has_benefits = True
        
        # Additional info
        if package.get('eligibility'):
            st.markdown("**📋 Điều kiện:**")
            st.caption(package['eligibility'])
        
        if package.get('renewal_policy'):
            st.markdown("**🔄 Chính sách gia hạn:**")
            st.caption(package['renewal_policy'])
        
        # Variants and related packages
        if package.get('variants'):
            try:
                import ast
                variants = ast.literal_eval(package['variants']) if isinstance(package['variants'], str) else package['variants']
                if variants:
                    with st.expander("🔄 Các biến thể"):
                        if isinstance(variants, list):
                            for variant in variants[:5]:  # Show first 5
                                if isinstance(variant, dict):
                                    st.write(f"- {variant.get('code', 'N/A')}: {variant.get('full_name', 'N/A')}")
            except:
                pass
        
        if package.get('related_packages'):
            try:
                import ast
                related = ast.literal_eval(package['related_packages']) if isinstance(package['related_packages'], str) else package['related_packages']
                if related:
                    with st.expander("🔗 Gói liên quan"):
                        if isinstance(related, list):
                            for rel in related[:5]:  # Show first 5
                                if isinstance(rel, dict):
                                    code = rel.get('code', 'N/A')
                                    name = rel.get('full_name', 'N/A')
                                    url = rel.get('url', '')
                                    if url:
                                        st.write(f"- [{code}]({url}): {name}")
                                    else:
                                        st.write(f"- {code}: {name}")
            except:
                pass
        
        # Notes (if different from description)
        if package.get('notes') and package.get('notes') != package.get('description', ''):
            with st.expander("📝 Ghi chú"):
                st.text(package['notes'])
        
        # Registration info (original format)
        if package.get('registration') and package.get('registration') != package.get('registration_syntax', ''):
            try:
                import ast
                reg_info = package.get('registration', '')
                if isinstance(reg_info, str) and reg_info.startswith('{'):
                    reg_dict = ast.literal_eval(reg_info)
                    if isinstance(reg_dict, dict):
                        with st.expander("📋 Thông tin đăng ký đầy đủ"):
                            for key, value in reg_dict.items():
                                st.write(f"**{key}:** {value}")
            except:
                pass
        
        # Original link
        if package.get('original_link'):
            st.markdown(f"**🔗 Link gốc:** [{package['original_link']}]({package['original_link']})")
        elif package.get('source_url'):
            st.markdown(f"**🔗 URL nguồn:** [{package['source_url']}]({package['source_url']})")
        
        # Source file and relationship type
        col_meta1, col_meta2 = st.columns(2)
        with col_meta1:
            if package.get('source_file'):
                st.caption(f"📄 File nguồn: {package['source_file']}")
        with col_meta2:
            if package.get('relationship_type'):
                st.caption(f"🔗 Loại quan hệ: {package['relationship_type']}")
        
        # Show original column values if they differ from mapped ones
        with st.expander("📊 Thông tin gốc (nếu khác)"):
            original_fields = {
                'code': 'Mã gói gốc',
                'full_name': 'Tên đầy đủ gốc',
                'cycle': 'Chu kỳ gốc',
                'data_size': 'Dung lượng gốc',
                'source_url': 'URL nguồn gốc',
                'registration': 'Thông tin đăng ký gốc'
            }
            for field, label in original_fields.items():
                if package.get(field):
                    mapped_field = {
                        'code': 'package_code',
                        'full_name': 'package_name',
                        'cycle': 'cycle_days',
                        'data_size': 'data_gb',
                        'source_url': 'original_link',
                        'registration': 'registration_syntax'
                    }.get(field)
                    
                    # Only show if different from mapped value
                    if mapped_field:
                        mapped_value = package.get(mapped_field, '')
                        original_value = package.get(field, '')
                        if str(original_value) != str(mapped_value) and original_value:
                            st.write(f"**{label}:** {original_value}")
                    else:
                        st.write(f"**{label}:** {package.get(field)}")


def main():
    """Main application"""
    
    # Header
    st.markdown('<div class="main-header">📦 Package Search & Report Tool</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Create tabs for different datasets
    tab1, tab2 = st.tabs(["📊 Package Details (full_packages_map.csv)", "📋 All Codes (all_codes.csv)"])
    
    with tab1:
        render_packages_tab()
    
    with tab2:
        render_all_codes_tab()
    
    # Footer
    st.markdown("---")
    st.caption("📦 Package Search & Report Tool | Powered by Streamlit & RapidFuzz")


def render_packages_tab():
    """Render the main packages tab"""
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
            
            # Get all columns except internal search fields
            all_columns = list(display_df.columns)
            internal_fields = ['_similarity_score', '_match_field', '_search_string']
            
            # Start with all columns, but put similarity score first if it exists
            display_columns = []
            if '_similarity_score' in all_columns:
                display_columns.append('_similarity_score')
            
            # Add all other columns (excluding internal fields except similarity)
            for col in all_columns:
                if col not in internal_fields and col not in display_columns:
                    display_columns.append(col)
            
            # Add full description if requested and not already included
            if show_full_desc:
                if 'full_description' not in display_columns:
                    if 'full_description' in display_df.columns:
                        display_columns.append('full_description')
                    elif 'notes' in display_df.columns:
                        display_columns.append('notes')
                    elif 'description' in display_df.columns:
                        display_columns.append('description')
            
            # Format display
            display_df_formatted = display_df[display_columns].copy()
            
            # Rename columns - comprehensive mapping for all columns
            column_names = {
                '_similarity_score': 'Score (%)',
                # Mapped columns
                'package_code': 'Mã gói',
                'package_name': 'Tên gói',
                'source': 'Nguồn',
                'price': 'Giá (VNĐ)',
                'cycle_days': 'Chu kỳ (ngày)',
                'duration': 'Thời gian hiệu lực',
                'data_gb': 'Data (GB)',
                'data_limit_behavior': 'Hết data',
                'package_type': 'Loại gói',
                'description': 'Mô tả',
                'full_description': 'Mô tả chi tiết',
                'registration_syntax': 'Cú pháp ĐK',
                'cancellation_syntax': 'Cú pháp hủy',
                'check_syntax': 'Cú pháp tra cứu',
                'eligibility': 'Điều kiện',
                'renewal_policy': 'Chính sách GH',
                'support_hotline': 'Hotline',
                'original_link': 'Link gốc',
                'benefits': 'Lợi ích',
                'variants': 'Biến thể',
                'related_packages': 'Gói liên quan',
                'benefit_free_internal_calls': 'Gọi nội mạng',
                'benefit_free_external_calls': 'Gọi ngoại mạng',
                'benefit_free_sms': 'SMS miễn phí',
                'benefit_free_social_media_data': 'Data MXH',
                'benefit_free_tv': 'TV miễn phí',
                'benefit_other_benefits': 'Lợi ích khác',
                'source_file': 'File nguồn',
                'relationship_type': 'Loại quan hệ',
                'voice_minutes': 'Phút gọi',
                'sms_count': 'SMS',
                # Original column names (keep as is if not mapped)
                'code': 'Mã gói (gốc)',
                'full_name': 'Tên đầy đủ',
                'cycle': 'Chu kỳ',
                'data_size': 'Dung lượng data',
                'source_url': 'URL nguồn',
                'registration': 'Đăng ký',
                'notes': 'Ghi chú'
            }
            # Rename columns - only rename if mapping exists, keep original name otherwise
            display_df_formatted.rename(columns={k: v for k, v in column_names.items() if k in display_df_formatted.columns}, inplace=True)
            
            # Truncate full description if present
            if show_full_desc and 'Mô tả chi tiết' in display_df_formatted.columns:
                display_df_formatted['Mô tả chi tiết'] = display_df_formatted['Mô tả chi tiết'].apply(
                    lambda x: (str(x)[:max_desc_length] + '...') if pd.notna(x) and len(str(x)) > max_desc_length else str(x) if pd.notna(x) else '-'
                )
            
            # Format numbers
            price_col = 'Giá (VNĐ)' if 'Giá (VNĐ)' in display_df_formatted.columns else 'Giá (đ)'
            if price_col in display_df_formatted.columns:
                display_df_formatted[price_col] = display_df_formatted[price_col].apply(
                    lambda x: f"{x:,.0f}" if pd.notna(x) else '-'
                )
            
            # Format cycle_days
            if 'Chu kỳ (ngày)' in display_df_formatted.columns:
                display_df_formatted['Chu kỳ (ngày)'] = display_df_formatted['Chu kỳ (ngày)'].apply(
                    lambda x: format_cycle(x) if pd.notna(x) else '-'
                )
            
            # Format duration
            if 'Thời gian hiệu lực' in display_df_formatted.columns:
                display_df_formatted['Thời gian hiệu lực'] = display_df_formatted['Thời gian hiệu lực'].apply(
                    lambda x: format_cycle(x) if pd.notna(x) else '-'
                )
            
            # Adjust height based on number of columns and whether full description is shown
            num_cols = len(display_df_formatted.columns)
            table_height = min(800, max(400, 200 + num_cols * 30)) if show_full_desc else min(600, max(300, 150 + num_cols * 20))
            
            # Configure column widths for text columns
            column_config = {}
            text_columns = ['Mô tả', 'Mô tả chi tiết', 'Lợi ích', 'Biến thể', 'Gói liên quan', 
                          'Ghi chú', 'Điều kiện', 'Chính sách GH', 'URL nguồn', 'Thông tin đăng ký gốc']
            for col in text_columns:
                if col in display_df_formatted.columns:
                    column_config[col] = st.column_config.TextColumn(
                        col,
                        width="large" if col in ['Mô tả chi tiết', 'Lợi ích', 'Biến thể', 'Gói liên quan'] else "medium",
                        help="Click vào row để xem full text"
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


def render_all_codes_tab():
    """Render the all codes tab"""
    # Load all codes data
    with st.spinner("Đang tải dữ liệu all_codes..."):
        df_codes, stats_codes = load_all_codes()
        codes_search_engine = create_codes_search_engine(df_codes)
    
    # Sidebar - Statistics
    with st.sidebar:
        st.header("📊 Thống kê All Codes")
        st.metric("Tổng số mã gói", f"{stats_codes['total_codes']:,}")
        st.metric("Mã unique", f"{stats_codes['unique_codes']:,}")
    
    # Main content
    st.subheader("🔍 Tìm kiếm mã gói")
    
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        # Get preset value if button was clicked
        preset_value = st.session_state.get("search_query_codes_value", "")
        
        # If there's a preset value, delete the widget key to reset it
        if preset_value and 'search_input_codes' in st.session_state:
            del st.session_state.search_input_codes
        
        search_query_codes = st.text_input(
            "Nhập mã gói cần tìm",
            placeholder="Ví dụ: D15, BIG, 5G150... hoặc regex: ^MI_.*150.*$",
            help="Fuzzy: tìm gần đúng | Regex: tìm theo pattern",
            key="search_input_codes",
            value=preset_value if preset_value else ""
        )
        
        # Clear preset value after using it
        if preset_value:
            st.session_state.search_query_codes_value = ""
    
    with col2:
        search_mode_codes = st.selectbox(
            "Chế độ tìm",
            options=["Fuzzy", "Regex"],
            help="Fuzzy: Tìm gần đúng | Regex: Tìm theo pattern",
            key="search_mode_codes"
        )
    
    with col3:
        max_results = st.number_input(
            "Số kết quả",
            min_value=5,
            max_value=500,
            value=50,
            step=5,
            key="max_results_codes"
        )
    
    # Search mode specific options
    search_threshold_codes = 70  # default
    case_sensitive_codes = False  # default
    
    if search_mode_codes == "Regex":
        col_regex1, col_regex2 = st.columns(2)
        with col_regex1:
            st.caption("💡 Ví dụ regex: `^MI_D.*` (bắt đầu MI_D) | `.*15.*` (chứa 15) | `^MI_(BIG|YOLO).*`")
        with col_regex2:
            case_sensitive_codes = st.checkbox("Case sensitive", value=False, key="case_codes")
    else:
        # Fuzzy search - show threshold and suggestions
        search_threshold_codes = st.slider(
            "Độ chính xác tìm kiếm (%)",
            min_value=50,
            max_value=100,
            value=70,
            step=5,
            help="Độ tương đồng tối thiểu với từ khóa tìm kiếm",
            key="threshold_codes"
        )
        
        # Show suggestions
        if search_query_codes and len(search_query_codes) >= 1:
            try:
                suggestions = codes_search_engine.get_suggestions(search_query_codes, limit=5)
                if suggestions:
                    st.caption(f"💡 Gợi ý: {', '.join(suggestions[:5])}")
            except:
                pass
    
    # Initialize session state for codes results
    if 'codes_search_results' not in st.session_state:
        st.session_state.codes_search_results = []
    
    # Search buttons
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 4])
    
    with col_btn1:
        search_button_codes = st.button("🔍 Tìm kiếm", type="primary", use_container_width=True, key="search_codes_btn")
    
    with col_btn2:
        show_all_codes = st.button("📋 Show All", use_container_width=True, key="show_all_codes_btn")
    
    with col_btn3:
        clear_codes = st.button("🗑️ Xóa", use_container_width=True, key="clear_codes_btn")
    
    if clear_codes:
        st.session_state.codes_search_results = []
        st.rerun()
    
    # Show all codes
    if show_all_codes:
        st.session_state.codes_search_results = df_codes.to_dict('records')
        if 'codes_current_page' not in st.session_state:
            st.session_state.codes_current_page = 1
        st.rerun()
    
    # Perform search - trigger on button or when there's a query
    perform_search = search_button_codes or (search_query_codes and search_query_codes.strip())
    
    if perform_search and search_query_codes and search_query_codes.strip():
        with st.spinner("Đang tìm kiếm..."):
            try:
                if search_mode_codes == "Fuzzy":
                    # Use fuzzy search - only search in package_code
                    results_list = codes_search_engine.search(
                        query=search_query_codes,
                        top_n=max_results,
                        threshold=search_threshold_codes,
                        search_in='code'
                    )
                    st.session_state.codes_search_results = results_list
                    
                elif search_mode_codes == "Regex":
                    # Use regex search
                    try:
                        results_list = codes_search_engine.search_regex(
                            pattern=search_query_codes,
                            search_in='code',
                            case_sensitive=case_sensitive_codes,
                            top_n=max_results
                        )
                        st.session_state.codes_search_results = results_list
                        if not results_list:
                            st.info(f"💡 Pattern '{search_query_codes}' không match với code nào. Thử pattern khác hoặc dùng fuzzy search.")
                    except Exception as e:
                        st.error(f"❌ Lỗi regex: {str(e)}")
                        st.session_state.codes_search_results = []
            except Exception as e:
                st.error(f"❌ Lỗi tìm kiếm: {str(e)}")
                st.session_state.codes_search_results = []
    
    # Display results
    results_codes = st.session_state.codes_search_results
    
    if results_codes:
        # Show score for fuzzy search
        show_score = search_mode_codes == "Fuzzy" and '_similarity_score' in results_codes[0] if results_codes else False
        
        st.markdown(f'<div class="result-count">✅ Tìm thấy {len(results_codes)} mã gói</div>', unsafe_allow_html=True)
        
        # Pagination settings
        col_view1, col_view2, col_view3 = st.columns([2, 2, 2])
        
        with col_view1:
            view_mode_codes = st.radio(
                "Chế độ hiển thị:",
                options=["📋 Bảng", "📇 Danh sách"],
                horizontal=True,
                key="view_mode_codes"
            )
        
        with col_view2:
            if len(results_codes) > 50:
                use_pagination_codes = st.checkbox("Sử dụng phân trang", value=True, key="pagination_codes")
            else:
                use_pagination_codes = False
        
        with col_view3:
            if use_pagination_codes:
                page_size_codes = st.selectbox(
                    "Số mã/trang:",
                    options=[50, 100, 200, 500],
                    index=0,
                    key="page_size_codes"
                )
        
        # Pagination logic
        if use_pagination_codes:
            total_pages_codes = (len(results_codes) - 1) // page_size_codes + 1
            
            if 'codes_current_page' not in st.session_state:
                st.session_state.codes_current_page = 1
            
            # Page navigation
            col_nav1, col_nav2, col_nav3, col_nav4, col_nav5 = st.columns([1, 1, 2, 1, 1])
            
            with col_nav1:
                if st.button("⏮️ Đầu", disabled=(st.session_state.codes_current_page == 1), key="first_codes"):
                    st.session_state.codes_current_page = 1
                    st.rerun()
            
            with col_nav2:
                if st.button("◀️ Trước", disabled=(st.session_state.codes_current_page == 1), key="prev_codes"):
                    st.session_state.codes_current_page -= 1
                    st.rerun()
            
            with col_nav3:
                st.markdown(f"<div style='text-align: center; padding: 0.5rem;'>Trang {st.session_state.codes_current_page} / {total_pages_codes}</div>", unsafe_allow_html=True)
            
            with col_nav4:
                if st.button("▶️ Sau", disabled=(st.session_state.codes_current_page == total_pages_codes), key="next_codes"):
                    st.session_state.codes_current_page += 1
                    st.rerun()
            
            with col_nav5:
                if st.button("⏭️ Cuối", disabled=(st.session_state.codes_current_page == total_pages_codes), key="last_codes"):
                    st.session_state.codes_current_page = total_pages_codes
                    st.rerun()
            
            # Get current page results
            start_idx = (st.session_state.codes_current_page - 1) * page_size_codes
            end_idx = min(start_idx + page_size_codes, len(results_codes))
            paginated_results_codes = results_codes[start_idx:end_idx]
            
            st.caption(f"Hiển thị {start_idx + 1}-{end_idx} trong tổng số {len(results_codes)} mã")
        else:
            paginated_results_codes = results_codes
        
        if view_mode_codes == "📋 Bảng":
            # Table view
            display_df_codes = pd.DataFrame(paginated_results_codes)
            
            # Configure columns based on available data
            column_config = {
                "package_code": st.column_config.TextColumn(
                    "Mã gói",
                    width="large",
                    help="Mã gói cước"
                )
            }
            
            # Add similarity score column if available
            if '_similarity_score' in display_df_codes.columns and show_score:
                display_df_codes = display_df_codes[['_similarity_score', 'package_code']]
                display_df_codes.rename(columns={'_similarity_score': 'Score (%)'}, inplace=True)
                column_config['Score (%)'] = st.column_config.NumberColumn(
                    "Score (%)",
                    help="Độ tương đồng với từ khóa tìm kiếm",
                    format="%.1f%%"
                )
            else:
                # Only show package_code
                display_df_codes = display_df_codes[['package_code']]
            
            st.dataframe(
                display_df_codes,
                use_container_width=True,
                hide_index=True,
                height=400,
                column_config=column_config
            )
        else:
            # List view - display as a grid
            cols_per_row = 4
            
            for i in range(0, len(paginated_results_codes), cols_per_row):
                cols = st.columns(cols_per_row)
                for j, col in enumerate(cols):
                    if i + j < len(paginated_results_codes):
                        item = paginated_results_codes[i + j]
                        with col:
                            if show_score and '_similarity_score' in item:
                                st.caption(f"Score: {item['_similarity_score']:.1f}%")
                            st.code(item['package_code'], language=None)
        
        # Export section
        st.markdown("---")
        st.subheader("📥 Xuất kết quả")
        
        col_export1, col_export2 = st.columns(2)
        
        with col_export1:
            if st.button("📄 Export to CSV", use_container_width=True, key="export_csv_codes"):
                try:
                    df_export_codes = pd.DataFrame(results_codes)
                    csv_data_codes = df_export_codes.to_csv(index=False, encoding='utf-8-sig')
                    
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"all_codes_filtered_{timestamp}.csv"
                    
                    st.download_button(
                        label="💾 Tải xuống CSV",
                        data=csv_data_codes.encode('utf-8-sig'),
                        file_name=filename,
                        mime="text/csv",
                        key="download_csv_codes"
                    )
                    
                    st.success(f"✅ File CSV đã sẵn sàng! ({len(results_codes):,} mã)")
                    
                except Exception as e:
                    st.error(f"❌ Lỗi khi tạo CSV: {e}")
        
        with col_export2:
            if st.button("📋 Export to Text", use_container_width=True, key="export_txt_codes"):
                try:
                    codes_text = "\n".join([item['package_code'] for item in results_codes])
                    
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"all_codes_list_{timestamp}.txt"
                    
                    st.download_button(
                        label="💾 Tải xuống Text",
                        data=codes_text,
                        file_name=filename,
                        mime="text/plain",
                        key="download_txt_codes"
                    )
                    
                    st.success(f"✅ File Text đã sẵn sàng! ({len(results_codes):,} mã)")
                    
                except Exception as e:
                    st.error(f"❌ Lỗi khi tạo Text: {e}")
    
    elif search_query_codes and search_query_codes.strip():
        st.warning(f"⚠️ Không tìm thấy mã gói phù hợp cho '{search_query_codes}'")
        st.info("💡 Thử:\n- Giảm threshold nếu dùng Fuzzy\n- Kiểm tra regex pattern nếu dùng Regex\n- Chuyển sang mode tìm kiếm khác")
    else:
        st.info("💡 Nhập mã gói để bắt đầu tìm kiếm, hoặc click **📋 Show All** để xem toàn bộ!")
        
        # Show search examples
        st.subheader("📌 Ví dụ tìm kiếm")
        
        col_ex1, col_ex2 = st.columns(2)
        
        with col_ex1:
            st.markdown("**Fuzzy Search:**")
            fuzzy_examples = [
                ("D15", "Tìm codes chứa D15"),
                ("BIG", "Tìm codes chứa BIG"),
                ("YOLO", "Tìm codes chứa YOLO"),
                ("5G150", "Tìm codes chứa 5G150")
            ]
            for query, desc in fuzzy_examples:
                if st.button(f"🔍 `{query}` - {desc}", key=f"ex_fuzzy_{query}", use_container_width=True):
                    # Set the value in session state, which will be used by text_input
                    st.session_state.search_query_codes_value = query
                    # Clear the widget's internal state by rerunning
                    if 'search_input_codes' in st.session_state:
                        del st.session_state.search_input_codes
                    st.rerun()
        
        with col_ex2:
            st.markdown("**Regex Search:**")
            regex_examples = [
                ("^MI_D.*", "Bắt đầu với MI_D"),
                (".*150.*", "Chứa 150"),
                ("^MI_BIG.*", "Bắt đầu với MI_BIG"),
                (".*YOLO.*", "Chứa YOLO")
            ]
            for pattern, desc in regex_examples:
                if st.button(f"🔍 `{pattern}` - {desc}", key=f"ex_regex_{pattern.replace('.', '_').replace('*', 'x')}", use_container_width=True):
                    # Set the value in session state, which will be used by text_input
                    st.session_state.search_query_codes_value = pattern
                    # Clear the widget's internal state by rerunning
                    if 'search_input_codes' in st.session_state:
                        del st.session_state.search_input_codes
                    st.rerun()
        
        # Show some sample codes
        st.markdown("---")
        st.markdown("**Một số mã gói mẫu:**")
        sample_codes = df_codes.head(15)['package_code'].tolist()
        
        cols_sample = st.columns(5)
        for idx, code in enumerate(sample_codes):
            with cols_sample[idx % 5]:
                st.code(code, language=None)


if __name__ == "__main__":
    main()
