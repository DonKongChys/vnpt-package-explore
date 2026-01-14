"""
Quick test to verify full_description is in data
"""

from data_loader import PackageDataLoader
import pandas as pd

print("=" * 60)
print("Testing Full Description in Data")
print("=" * 60)

try:
    # Load data
    loader = PackageDataLoader("unified_packages_clean.csv")
    df = loader.load_data()
    
    print(f"\n✅ Loaded {len(df)} packages")
    print(f"\n📋 Columns in DataFrame:")
    for i, col in enumerate(df.columns, 1):
        print(f"   {i}. {col}")
    
    # Check if full_description exists
    if 'full_description' in df.columns:
        print(f"\n✅ Column 'full_description' exists")
        
        # Check some samples
        sample = df.head(3)
        print(f"\n📊 Sample full_description values:")
        for idx, row in sample.iterrows():
            code = row['package_code']
            desc = str(row['full_description'])
            desc_len = len(desc)
            preview = desc[:100] if len(desc) > 100 else desc
            print(f"\n   Package: {code}")
            print(f"   Length: {desc_len} chars")
            print(f"   Preview: {preview}...")
        
        # Check how many have non-empty full_description
        non_empty = df['full_description'].notna().sum()
        print(f"\n✅ Packages with full_description: {non_empty:,} / {len(df):,}")
        
    else:
        print(f"\n❌ Column 'full_description' NOT FOUND!")
        print("   Available columns:", list(df.columns))
    
    print("\n" + "=" * 60)
    print("✅ Test completed")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
