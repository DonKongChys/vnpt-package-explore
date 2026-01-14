"""
Simple verification script to check if everything is in place
No external dependencies required
"""

import sys
from pathlib import Path

print("=" * 70)
print("📦 Package Search & Report Tool - Setup Verification")
print("=" * 70)

errors = []
warnings = []

# Check 1: Files exist
print("\n1️⃣ Checking required files...")
required_files = [
    "unified_packages_clean.csv",
    "app.py",
    "data_loader.py",
    "search_engine.py",
    "report_generator.py",
    "requirements.txt",
    "README.md"
]

for file in required_files:
    path = Path(file)
    if path.exists():
        size = path.stat().st_size
        print(f"   ✅ {file} ({size:,} bytes)")
    else:
        print(f"   ❌ {file} NOT FOUND")
        errors.append(f"Missing file: {file}")

# Check 2: CSV file structure
print("\n2️⃣ Checking CSV file...")
csv_path = Path("unified_packages_clean.csv")
if csv_path.exists():
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            header = f.readline().strip()
            line_count = sum(1 for _ in f) + 1  # +1 for header
            
        expected_columns = [
            'source', 'package_code', 'package_name', 'price', 'cycle_days',
            'data_gb', 'voice_minutes', 'sms_count', 'package_type',
            'description', 'full_description', 'registration_syntax',
            'cancellation_syntax', 'check_syntax', 'eligibility',
            'renewal_policy', 'support_hotline', 'original_link'
        ]
        
        print(f"   ✅ CSV has {line_count:,} lines (including header)")
        print(f"   ✅ Header: {header[:100]}...")
        
        # Check if expected columns are present
        for col in expected_columns[:5]:  # Check first 5
            if col in header:
                print(f"   ✅ Column '{col}' present")
            else:
                warnings.append(f"Column '{col}' might be missing")
                
    except Exception as e:
        print(f"   ⚠️ Error reading CSV: {e}")
        warnings.append(f"CSV read error: {e}")
else:
    print(f"   ❌ CSV file not found")
    errors.append("CSV file missing")

# Check 3: Python modules syntax
print("\n3️⃣ Checking Python module syntax...")
modules = ["app.py", "data_loader.py", "search_engine.py", "report_generator.py"]

for module in modules:
    path = Path(module)
    if path.exists():
        try:
            with open(path, 'r', encoding='utf-8') as f:
                code = f.read()
                compile(code, module, 'exec')
            print(f"   ✅ {module} - syntax OK")
        except SyntaxError as e:
            print(f"   ❌ {module} - syntax error: {e}")
            errors.append(f"Syntax error in {module}")
    else:
        print(f"   ⚠️ {module} - not found (already reported)")

# Check 4: Dependencies listed
print("\n4️⃣ Checking requirements.txt...")
req_path = Path("requirements.txt")
if req_path.exists():
    with open(req_path, 'r') as f:
        deps = f.read().strip().split('\n')
    
    required_deps = ['streamlit', 'pandas', 'openpyxl', 'rapidfuzz']
    
    for dep in required_deps:
        found = any(dep in line.lower() for line in deps)
        if found:
            print(f"   ✅ {dep} listed")
        else:
            print(f"   ⚠️ {dep} not found")
            warnings.append(f"Dependency {dep} not in requirements.txt")

# Check 5: Directory structure
print("\n5️⃣ Checking directory structure...")
current_dir = Path.cwd()
print(f"   ℹ️ Current directory: {current_dir}")
print(f"   ℹ️ Files in directory: {len(list(current_dir.iterdir()))}")

# Summary
print("\n" + "=" * 70)
if errors:
    print("❌ VERIFICATION FAILED")
    print("\nErrors found:")
    for error in errors:
        print(f"  • {error}")
else:
    print("✅ VERIFICATION PASSED")

if warnings:
    print("\nWarnings:")
    for warning in warnings:
        print(f"  ⚠️ {warning}")

print("=" * 70)

# Next steps
if not errors:
    print("\n📋 Next Steps:")
    print("  1. conda activate py312")
    print("  2. pip install -r requirements.txt")
    print("  3. python test_modules.py  (to test with dependencies)")
    print("  4. streamlit run app.py    (to run the web UI)")
    print("")
    print("Or use the convenience script:")
    print("  bash run_tests.sh")
else:
    print("\n⚠️ Please fix the errors above before proceeding.")
    sys.exit(1)

print("=" * 70)
