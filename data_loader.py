"""
Data Loader Module
Load and cache package data from CSV file
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PackageDataLoader:
    """Load and manage package data from CSV"""
    
    def __init__(self, csv_path: str = "unified_packages_clean.csv"):
        """
        Initialize data loader
        
        Args:
            csv_path: Path to CSV file (relative or absolute)
        """
        self.csv_path = Path(csv_path)
        self._data: Optional[pd.DataFrame] = None
        self._validate_file()
        
    def _validate_file(self):
        """Validate CSV file exists"""
        if not self.csv_path.exists():
            raise FileNotFoundError(
                f"CSV file not found: {self.csv_path}\n"
                f"Please ensure unified_packages_clean.csv is in the correct location."
            )
    
    def load_data(self, force_reload: bool = False) -> pd.DataFrame:
        """
        Load data from CSV with caching
        
        Args:
            force_reload: Force reload data even if cached
            
        Returns:
            DataFrame with package data
        """
        if self._data is None or force_reload:
            logger.info(f"Loading data from {self.csv_path}")
            try:
                self._data = pd.read_csv(self.csv_path)
                self._clean_data()
                logger.info(f"Loaded {len(self._data)} packages successfully")
            except Exception as e:
                logger.error(f"Error loading CSV: {e}")
                raise
        
        return self._data
    
    def _clean_data(self):
        """Clean and prepare data"""
        if self._data is None:
            return
        
        # Convert numeric columns
        numeric_cols = ['price', 'cycle_days', 'data_gb', 'sms_count']
        for col in numeric_cols:
            if col in self._data.columns:
                self._data[col] = pd.to_numeric(self._data[col], errors='coerce')
        
        # Fill NaN values for string columns
        string_cols = [
            'package_code', 'package_name', 'description', 'full_description',
            'registration_syntax', 'cancellation_syntax', 'check_syntax',
            'eligibility', 'renewal_policy', 'support_hotline', 'original_link'
        ]
        for col in string_cols:
            if col in self._data.columns:
                self._data[col] = self._data[col].fillna('')
        
        # Ensure package_code is string and strip whitespace
        if 'package_code' in self._data.columns:
            self._data['package_code'] = self._data['package_code'].astype(str).str.strip()
        
        if 'package_name' in self._data.columns:
            self._data['package_name'] = self._data['package_name'].astype(str).str.strip()
    
    def get_all_packages(self) -> List[Dict]:
        """
        Get all packages as list of dictionaries
        
        Returns:
            List of package dictionaries
        """
        df = self.load_data()
        return df.to_dict('records')
    
    def get_package_by_code(self, code: str) -> Optional[Dict]:
        """
        Get single package by exact code match
        
        Args:
            code: Package code to search for
            
        Returns:
            Package dictionary or None if not found
        """
        df = self.load_data()
        matches = df[df['package_code'].str.upper() == code.upper()]
        
        if len(matches) == 0:
            return None
        
        return matches.iloc[0].to_dict()
    
    def get_packages_by_source(self, source: str) -> List[Dict]:
        """
        Get packages filtered by source
        
        Args:
            source: Source name (myvnpt, vinaphone, digishop)
            
        Returns:
            List of package dictionaries
        """
        df = self.load_data()
        filtered = df[df['source'].str.lower() == source.lower()]
        return filtered.to_dict('records')
    
    def get_packages_by_price_range(
        self, 
        min_price: Optional[float] = None,
        max_price: Optional[float] = None
    ) -> List[Dict]:
        """
        Get packages within price range
        
        Args:
            min_price: Minimum price (inclusive)
            max_price: Maximum price (inclusive)
            
        Returns:
            List of package dictionaries
        """
        df = self.load_data()
        
        if min_price is not None:
            df = df[df['price'] >= min_price]
        
        if max_price is not None:
            df = df[df['price'] <= max_price]
        
        return df.to_dict('records')
    
    def get_statistics(self) -> Dict:
        """
        Get statistics about the dataset
        
        Returns:
            Dictionary with statistics
        """
        df = self.load_data()
        
        stats = {
            'total_packages': len(df),
            'sources': df['source'].value_counts().to_dict(),
            'price_stats': {
                'min': float(df['price'].min()) if not df['price'].isna().all() else 0,
                'max': float(df['price'].max()) if not df['price'].isna().all() else 0,
                'mean': float(df['price'].mean()) if not df['price'].isna().all() else 0,
                'median': float(df['price'].median()) if not df['price'].isna().all() else 0,
            },
            'data_stats': {
                'min_gb': float(df['data_gb'].min()) if not df['data_gb'].isna().all() else 0,
                'max_gb': float(df['data_gb'].max()) if not df['data_gb'].isna().all() else 0,
                'mean_gb': float(df['data_gb'].mean()) if not df['data_gb'].isna().all() else 0,
            },
            'cycle_stats': {
                'min_days': float(df['cycle_days'].min()) if not df['cycle_days'].isna().all() else 0,
                'max_days': float(df['cycle_days'].max()) if not df['cycle_days'].isna().all() else 0,
            }
        }
        
        # Package types distribution
        if 'package_type' in df.columns:
            stats['package_types'] = df['package_type'].value_counts().to_dict()
        
        return stats
    
    def get_dataframe(self) -> pd.DataFrame:
        """
        Get raw DataFrame
        
        Returns:
            DataFrame with all data
        """
        return self.load_data()


# Convenience function for quick loading
def load_packages(csv_path: str = "unified_packages_clean.csv") -> PackageDataLoader:
    """
    Convenience function to create and return a data loader
    
    Args:
        csv_path: Path to CSV file
        
    Returns:
        PackageDataLoader instance
    """
    return PackageDataLoader(csv_path)


if __name__ == "__main__":
    # Test the data loader
    try:
        loader = PackageDataLoader()
        df = loader.load_data()
        print(f"✅ Loaded {len(df)} packages")
        
        stats = loader.get_statistics()
        print(f"\n📊 Statistics:")
        print(f"  Total packages: {stats['total_packages']}")
        print(f"  Sources: {stats['sources']}")
        print(f"  Price range: {stats['price_stats']['min']:,.0f} - {stats['price_stats']['max']:,.0f} VNĐ")
        
        # Test exact search
        package = loader.get_package_by_code("D15")
        if package:
            print(f"\n🔍 Found package D15:")
            print(f"  Name: {package['package_name']}")
            print(f"  Price: {package['price']:,.0f} VNĐ")
            print(f"  Data: {package['data_gb']} GB")
        
    except Exception as e:
        print(f"❌ Error: {e}")
