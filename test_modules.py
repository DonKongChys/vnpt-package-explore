"""
Test script for all modules
"""

import sys
from pathlib import Path

print("=" * 60)
print("Testing Package Search & Report Tool Modules")
print("=" * 60)

# Test 1: Data Loader
print("\n1️⃣ Testing Data Loader...")
try:
    from data_loader import PackageDataLoader
    
    loader = PackageDataLoader("unified_packages_clean.csv")
    df = loader.load_data()
    stats = loader.get_statistics()
    
    print(f"   ✅ Loaded {len(df)} packages")
    print(f"   ✅ Sources: {list(stats['sources'].keys())}")
    print(f"   ✅ Price range: {stats['price_stats']['min']:,.0f} - {stats['price_stats']['max']:,.0f} VNĐ")
    
    # Test exact search
    package = loader.get_package_by_code("D15")
    if package:
        print(f"   ✅ Found package D15: {package['package_name']}")
    else:
        print(f"   ⚠️ Package D15 not found")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Search Engine
print("\n2️⃣ Testing Search Engine...")
try:
    from search_engine import FuzzySearchEngine
    
    search = FuzzySearchEngine(df)
    
    # Test searches
    test_queries = ["D15", "BIG", "game"]
    
    for query in test_queries:
        results = search.search(query, top_n=5, threshold=60)
        print(f"   ✅ Search '{query}': found {len(results)} matches")
        if results:
            top_result = results[0]
            score = top_result.get('_similarity_score', 0)
            print(f"      Top: {top_result['package_code']} (Score: {score:.1f}%)")
    
    # Test exact match
    exact = search.exact_match("D15")
    if exact:
        print(f"   ✅ Exact match 'D15': {exact['package_code']}")
    
    # Test suggestions
    suggestions = search.get_suggestions("D", limit=5)
    print(f"   ✅ Suggestions for 'D': {', '.join(suggestions[:3])}...")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Report Generator
print("\n3️⃣ Testing Report Generator...")
try:
    from report_generator import ReportGenerator
    
    generator = ReportGenerator()
    
    # Get sample packages
    test_packages = df.head(10).to_dict('records')
    
    # Test CSV generation
    csv_path = "test_output.csv"
    generator.generate_csv(test_packages, csv_path)
    print(f"   ✅ CSV generated: {csv_path}")
    
    # Test Excel generation
    excel_path = "test_output.xlsx"
    generator.generate_excel(test_packages, excel_path)
    print(f"   ✅ Excel generated: {excel_path}")
    
    # Test summary
    summary_path = "test_summary.txt"
    generator.generate_summary_report(test_packages, summary_path)
    print(f"   ✅ Summary generated: {summary_path}")
    
    # Clean up test files
    Path(csv_path).unlink(missing_ok=True)
    Path(excel_path).unlink(missing_ok=True)
    Path(summary_path).unlink(missing_ok=True)
    print(f"   ✅ Cleaned up test files")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Integration Test
print("\n4️⃣ Testing Integration...")
try:
    # Search and export workflow
    search_query = "D15"
    results = search.search(search_query, top_n=5)
    
    if results:
        print(f"   ✅ Found {len(results)} results for '{search_query}'")
        
        # Test export with search results
        test_export_path = "test_search_results.xlsx"
        generator.generate_excel(results, test_export_path, include_similarity=True)
        
        if Path(test_export_path).exists():
            size = Path(test_export_path).stat().st_size
            print(f"   ✅ Exported results to Excel ({size:,} bytes)")
            Path(test_export_path).unlink()
        else:
            print(f"   ⚠️ Export file not created")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Final summary
print("\n" + "=" * 60)
print("✅ All tests passed successfully!")
print("=" * 60)
print("\nYou can now run the Streamlit app:")
print("  conda activate py312")
print("  cd report_tools")
print("  streamlit run app.py")
print("=" * 60)
