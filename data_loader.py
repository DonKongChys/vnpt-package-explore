"""
Data Loader Module
Load and cache package data from CSV file
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PackageDataLoader:
    """Load and manage package data from CSV"""
    
    def __init__(self, csv_path: str = "full_packages_map.csv"):
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
        
        # Map new column structure to old structure (keep both original and mapped names)
        column_mapping = {
            'code': 'package_code',
            'full_name': 'package_name',
            'cycle': 'cycle_days',
            'data_size': 'data_gb',
            'source_url': 'original_link',
            'description': 'description',
            'registration': 'registration_syntax',
            'package_type': 'package_type',
            'source': 'source',
            'duration': 'duration',
            'data_limit_behavior': 'data_limit_behavior',
            'benefits': 'benefits',
            'variants': 'variants',
            'related_packages': 'related_packages',
            'benefit_free_internal_calls': 'benefit_free_internal_calls',
            'benefit_free_external_calls': 'benefit_free_external_calls',
            'benefit_free_sms': 'benefit_free_sms',
            'benefit_free_social_media_data': 'benefit_free_social_media_data',
            'benefit_free_tv': 'benefit_free_tv',
            'benefit_other_benefits': 'benefit_other_benefits',
            'source_file': 'source_file',
            'relationship_type': 'relationship_type',
            'notes': 'notes'  # Keep notes as well
        }
        
        # Create mapped columns but keep original columns too
        for old_col, new_col in column_mapping.items():
            if old_col in self._data.columns:
                # Create mapped column if it doesn't exist
                if new_col not in self._data.columns:
                    self._data[new_col] = self._data[old_col]
                # Keep original column name as well (for display)
                if old_col != new_col:
                    # Original column already exists, no need to duplicate
                    pass
        
        # Handle full_description: use notes if available, otherwise use description
        if 'full_description' not in self._data.columns:
            if 'notes' in self._data.columns:
                self._data['full_description'] = self._data['notes']
            elif 'description' in self._data.columns:
                self._data['full_description'] = self._data['description']
            else:
                self._data['full_description'] = ''
        
        # Parse cycle_days from "360 ngày" format
        if 'cycle_days' in self._data.columns:
            def parse_cycle(cycle_str):
                if pd.isna(cycle_str) or cycle_str == '':
                    return None
                try:
                    # Try to extract number from "360 ngày" or "12 tháng"
                    cycle_str = str(cycle_str).strip()
                    if 'tháng' in cycle_str or 'thang' in cycle_str.lower():
                        # Extract number and multiply by 30
                        num = float(re.search(r'[\d.]+', cycle_str).group())
                        return num * 30
                    elif 'ngày' in cycle_str or 'ngay' in cycle_str.lower():
                        # Extract number
                        num = float(re.search(r'[\d.]+', cycle_str).group())
                        return num
                    else:
                        # Try direct conversion
                        return float(cycle_str)
                except:
                    return None
            
            self._data['cycle_days'] = self._data['cycle_days'].apply(parse_cycle)
        
        # Parse data_gb from "2GB" format
        if 'data_gb' in self._data.columns:
            def parse_data_size(data_str):
                if pd.isna(data_str) or data_str == '':
                    return None
                try:
                    data_str = str(data_str).strip().upper()
                    # Extract number from "2GB", "1.5GB", etc.
                    match = re.search(r'[\d.]+', data_str)
                    if match:
                        return float(match.group())
                    return None
                except:
                    return None
            
            self._data['data_gb'] = self._data['data_gb'].apply(parse_data_size)
        
        # Parse registration syntax from dict/json string
        if 'registration_syntax' in self._data.columns:
            def parse_registration(reg_str):
                if pd.isna(reg_str) or reg_str == '':
                    return ''
                try:
                    import ast
                    if isinstance(reg_str, str) and reg_str.startswith('{'):
                        reg_dict = ast.literal_eval(reg_str)
                        if isinstance(reg_dict, dict):
                            return reg_dict.get('sms_syntax', '')
                    return str(reg_str)
                except:
                    return str(reg_str)
            
            self._data['registration_syntax'] = self._data['registration_syntax'].apply(parse_registration)
        
        # Parse duration from "360 ngày" format (similar to cycle)
        if 'duration' in self._data.columns:
            def parse_duration(duration_str):
                if pd.isna(duration_str) or duration_str == '':
                    return None
                try:
                    duration_str = str(duration_str).strip()
                    if 'tháng' in duration_str or 'thang' in duration_str.lower():
                        num = float(re.search(r'[\d.]+', duration_str).group())
                        return num * 30
                    elif 'ngày' in duration_str or 'ngay' in duration_str.lower():
                        num = float(re.search(r'[\d.]+', duration_str).group())
                        return num
                    else:
                        return float(duration_str)
                except:
                    return None
            
            self._data['duration'] = self._data['duration'].apply(parse_duration)
        
        # Convert numeric columns
        numeric_cols = ['price', 'cycle_days', 'data_gb']
        for col in numeric_cols:
            if col in self._data.columns:
                self._data[col] = pd.to_numeric(self._data[col], errors='coerce')
        
        # Add missing columns with default values
        if 'voice_minutes' not in self._data.columns:
            self._data['voice_minutes'] = None
        if 'sms_count' not in self._data.columns:
            self._data['sms_count'] = None
        if 'cancellation_syntax' not in self._data.columns:
            self._data['cancellation_syntax'] = ''
        if 'check_syntax' not in self._data.columns:
            self._data['check_syntax'] = ''
        if 'eligibility' not in self._data.columns:
            self._data['eligibility'] = ''
        if 'renewal_policy' not in self._data.columns:
            self._data['renewal_policy'] = ''
        if 'support_hotline' not in self._data.columns:
            self._data['support_hotline'] = ''
        if 'duration' not in self._data.columns:
            self._data['duration'] = None
        if 'data_limit_behavior' not in self._data.columns:
            self._data['data_limit_behavior'] = ''
        if 'benefits' not in self._data.columns:
            self._data['benefits'] = ''
        if 'variants' not in self._data.columns:
            self._data['variants'] = ''
        if 'related_packages' not in self._data.columns:
            self._data['related_packages'] = ''
        if 'benefit_free_internal_calls' not in self._data.columns:
            self._data['benefit_free_internal_calls'] = ''
        if 'benefit_free_external_calls' not in self._data.columns:
            self._data['benefit_free_external_calls'] = ''
        if 'benefit_free_sms' not in self._data.columns:
            self._data['benefit_free_sms'] = ''
        if 'benefit_free_social_media_data' not in self._data.columns:
            self._data['benefit_free_social_media_data'] = ''
        if 'benefit_free_tv' not in self._data.columns:
            self._data['benefit_free_tv'] = ''
        if 'benefit_other_benefits' not in self._data.columns:
            self._data['benefit_other_benefits'] = ''
        if 'source_file' not in self._data.columns:
            self._data['source_file'] = ''
        if 'relationship_type' not in self._data.columns:
            self._data['relationship_type'] = ''
        
        # Fill NaN values for string columns
        string_cols = [
            'package_code', 'package_name', 'description', 'full_description',
            'registration_syntax', 'cancellation_syntax', 'check_syntax',
            'eligibility', 'renewal_policy', 'support_hotline', 'original_link',
            'data_limit_behavior', 'benefits', 'variants', 'related_packages',
            'benefit_free_internal_calls', 'benefit_free_external_calls',
            'benefit_free_sms', 'benefit_free_social_media_data',
            'benefit_free_tv', 'benefit_other_benefits', 'source_file',
            'relationship_type', 'package_type'
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
def load_packages(csv_path: str = "full_packages_map.csv") -> PackageDataLoader:
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
