"""
Quick test for regex search functionality
"""

import sys
from pathlib import Path

print("=" * 60)
print("Testing Regex Search Feature")
print("=" * 60)

try:
    from data_loader import PackageDataLoader
    from search_engine import FuzzySearchEngine
    
    # Load data
    print("\n1️⃣ Loading data...")
    loader = PackageDataLoader("unified_packages_clean.csv")
    df = loader.load_data()
    print(f"   ✅ Loaded {len(df)} packages")
    
    # Create search engine
    print("\n2️⃣ Creating search engine...")
    search = FuzzySearchEngine(df)
    print("   ✅ Search engine ready")
    
    # Test regex searches
    print("\n3️⃣ Testing regex searches...")
    
    test_cases = [
        ("^D15$", "code", "Exact match D15"),
        ("^D.*5$", "code", "Start with D, end with 5"),
        ("^BIG.*", "code", "Start with BIG"),
        (".*GAME.*", "both", "Contains GAME"),
        ("^(D|ST).*", "code", "Start with D or ST"),
    ]
    
    for pattern, field, description in test_cases:
        print(f"\n   Pattern: {pattern}")
        print(f"   Field: {field}")
        print(f"   Description: {description}")
        
        results = search.search_regex(
            pattern=pattern,
            search_in=field,
            case_sensitive=False,
            top_n=5
        )
        
        print(f"   → Found {len(results)} matches")
        if results:
            for i, pkg in enumerate(results[:3], 1):
                print(f"      {i}. {pkg['package_code']} - {pkg['package_name']}")
    
    # Test invalid regex
    print("\n4️⃣ Testing invalid regex...")
    results = search.search_regex(
        pattern="[invalid(regex",
        search_in="code",
        top_n=10
    )
    print(f"   → Returned {len(results)} results (should be 0 for invalid regex)")
    
    print("\n" + "=" * 60)
    print("✅ All regex tests completed!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
