"""
Fuzzy Search Engine Module
Search packages using fuzzy string matching
"""

import pandas as pd
from typing import Dict, List, Optional, Tuple
from rapidfuzz import fuzz, process
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)






class FuzzySearchEngine:
    """Fuzzy search engine for package data"""
    
    def __init__(self, data: pd.DataFrame):
        """
        Initialize search engine with data
        
        Args:
            data: DataFrame containing package data
        """
        self.data = data.copy()
        self._prepare_search_indices()
        
    def _prepare_search_indices(self):
        """Prepare search indices for faster lookup"""
        # Check if package_name column exists
        has_package_name = 'package_name' in self.data.columns
        
        # Create search strings combining code and name (if available)
        if has_package_name:
            self.data['_search_string'] = (
                self.data['package_code'].astype(str) + ' ' + 
                self.data['package_name'].astype(str)
            ).str.upper()
            self.package_names = self.data['package_name'].astype(str).tolist()
        else:
            # Only use package_code for search
            self.data['_search_string'] = self.data['package_code'].astype(str).str.upper()
            self.package_names = []
        
        # Create list of codes for rapid search
        self.package_codes = self.data['package_code'].astype(str).tolist()
        
    def search(
        self, 
        query: str, 
        top_n: int = 10,
        threshold: float = 60.0,
        search_in: str = 'both'  # 'code', 'name', or 'both'
    ) -> List[Dict]:
        """
        Fuzzy search for packages
        
        Args:
            query: Search query string
            top_n: Maximum number of results to return
            threshold: Minimum similarity score (0-100)
            search_in: Where to search ('code', 'name', or 'both')
            
        Returns:
            List of package dictionaries with similarity scores
        """
        if not query or query.strip() == '':
            return []
        
        query = query.strip().upper()
        results = []
        
        # Search in package codes
        if search_in in ['code', 'both']:
            code_matches = self._search_in_list(
                query, 
                self.package_codes, 
                threshold
            )
            for idx, score in code_matches:
                package = self.data.iloc[idx].to_dict()
                package['_similarity_score'] = score
                package['_match_field'] = 'package_code'
                results.append(package)
        
        # Search in package names (if available)
        if search_in in ['name', 'both'] and self.package_names:
            name_matches = self._search_in_list(
                query,
                self.package_names,
                threshold
            )
            for idx, score in name_matches:
                # Avoid duplicates
                if not any(r.get('package_code') == self.data.iloc[idx]['package_code'] 
                          for r in results):
                    package = self.data.iloc[idx].to_dict()
                    package['_similarity_score'] = score
                    package['_match_field'] = 'package_name'
                    results.append(package)
        
        # Sort by similarity score (descending)
        results.sort(key=lambda x: x['_similarity_score'], reverse=True)
        
        # Return top N results
        return results[:top_n]
    
    def _search_in_list(
        self,
        query: str,
        search_list: List[str],
        threshold: float
    ) -> List[Tuple[int, float]]:
        """
        Search in a list using fuzzy matching
        
        Args:
            query: Query string
            search_list: List of strings to search in
            threshold: Minimum similarity score
            
        Returns:
            List of (index, score) tuples
        """
        # Convert list items to uppercase for comparison
        search_list_upper = [str(item).upper() for item in search_list]
        
        # Use rapidfuzz process.extract for efficient fuzzy matching
        matches = process.extract(
            query,
            search_list_upper,
            scorer=fuzz.WRatio,  # Weighted ratio for better results
            limit=None  # Get all matches
        )
        
        # Filter by threshold and return with original indices
        results = []
        for match_text, score, idx in matches:
            if score >= threshold:
                results.append((idx, score))
        
        return results
    
    def search_by_code(
        self,
        code: str,
        threshold: float = 80.0,
        top_n: int = 10
    ) -> List[Dict]:
        """
        Search specifically by package code with higher threshold
        
        Args:
            code: Package code to search for
            threshold: Minimum similarity score (default 80 for codes)
            top_n: Maximum results
            
        Returns:
            List of matching packages
        """
        return self.search(code, top_n=top_n, threshold=threshold, search_in='code')
    
    def search_by_name(
        self,
        name: str,
        threshold: float = 70.0,
        top_n: int = 10
    ) -> List[Dict]:
        """
        Search specifically by package name
        
        Args:
            name: Package name to search for
            threshold: Minimum similarity score
            top_n: Maximum results
            
        Returns:
            List of matching packages
        """
        return self.search(name, top_n=top_n, threshold=threshold, search_in='name')
    
    def exact_match(self, code: str) -> Optional[Dict]:
        """
        Find exact match by code (case-insensitive)
        
        Args:
            code: Exact package code
            
        Returns:
            Package dictionary or None
        """
        code_upper = code.strip().upper()
        matches = self.data[self.data['package_code'].str.upper() == code_upper]
        
        if len(matches) > 0:
            package = matches.iloc[0].to_dict()
            package['_similarity_score'] = 100.0
            package['_match_field'] = 'exact'
            return package
        
        return None
    
    def search_with_filters(
        self,
        query: str,
        source: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_data: Optional[float] = None,
        max_data: Optional[float] = None,
        threshold: float = 60.0,
        top_n: int = 10
    ) -> List[Dict]:
        """
        Search with additional filters
        
        Args:
            query: Search query
            source: Filter by source (myvnpt, vinaphone, digishop)
            min_price: Minimum price filter
            max_price: Maximum price filter
            min_data: Minimum data (GB) filter
            max_data: Maximum data (GB) filter
            threshold: Similarity threshold
            top_n: Maximum results
            
        Returns:
            Filtered and matched packages
        """
        # Apply filters to data first
        filtered_data = self.data.copy()
        
        if source:
            filtered_data = filtered_data[
                filtered_data['source'].str.lower() == source.lower()
            ]
        
        if min_price is not None:
            filtered_data = filtered_data[filtered_data['price'] >= min_price]
        
        if max_price is not None:
            filtered_data = filtered_data[filtered_data['price'] <= max_price]
        
        if min_data is not None:
            filtered_data = filtered_data[filtered_data['data_gb'] >= min_data]
        
        if max_data is not None:
            filtered_data = filtered_data[filtered_data['data_gb'] <= max_data]
        
        # Create temporary search engine with filtered data
        temp_engine = FuzzySearchEngine(filtered_data)
        
        # Perform search on filtered data
        return temp_engine.search(query, top_n=top_n, threshold=threshold)
    
    def search_regex(
        self,
        pattern: str,
        search_in: str = 'both',  # 'code', 'name', 'both', 'description', 'all'
        case_sensitive: bool = False,
        top_n: int = 100
    ) -> List[Dict]:
        """
        Search using regular expressions
        
        Args:
            pattern: Regex pattern to search for
            search_in: Where to search ('code', 'name', 'both', 'description', 'all')
            case_sensitive: Whether to use case-sensitive matching
            top_n: Maximum number of results
            
        Returns:
            List of matching packages
        """
        if not pattern or pattern.strip() == '':
            return []
        
        try:
            # Compile regex pattern
            flags = 0 if case_sensitive else re.IGNORECASE
            regex = re.compile(pattern, flags)
        except re.error as e:
            logger.error(f"Invalid regex pattern: {e}")
            return []
        
        results = []
        
        # Search based on search_in parameter
        for idx, row in self.data.iterrows():
            match_found = False
            match_field = None
            
            if search_in in ['code', 'both', 'all']:
                code = str(row.get('package_code', ''))
                if code and code != 'nan' and regex.search(code):
                    match_found = True
                    match_field = 'package_code'
            
            if not match_found and search_in in ['name', 'both', 'all']:
                name = row.get('package_name', '')
                if pd.notna(name) and str(name) and str(name) != 'nan':
                    if regex.search(str(name)):
                        match_found = True
                        match_field = 'package_name'
            
            if not match_found and search_in in ['description', 'all']:
                desc = row.get('description', '')
                if pd.notna(desc) and str(desc) and str(desc) != 'nan':
                    if regex.search(str(desc)):
                        match_found = True
                        match_field = 'description'
            
            if not match_found and search_in == 'all':
                # Search in full description too
                full_desc = row.get('full_description', '')
                if pd.notna(full_desc) and str(full_desc) and str(full_desc) != 'nan':
                    if regex.search(str(full_desc)):
                        match_found = True
                        match_field = 'full_description'
            
            if match_found:
                package = row.to_dict()
                package['_similarity_score'] = 100.0  # Regex match is exact
                package['_match_field'] = match_field
                package['_search_type'] = 'regex'
                results.append(package)
                
                if len(results) >= top_n:
                    break
        
        return results
    
    def get_suggestions(self, partial_query: str, limit: int = 5) -> List[str]:
        """
        Get package code suggestions for autocomplete
        
        Args:
            partial_query: Partial query string
            limit: Maximum number of suggestions
            
        Returns:
            List of suggested package codes
        """
        if not partial_query or len(partial_query) < 1:
            return []
        
        partial_upper = partial_query.upper()
        
        # Find codes that start with the query
        starts_with = [
            code for code in self.package_codes 
            if str(code).upper().startswith(partial_upper)
        ]
        
        if len(starts_with) >= limit:
            return starts_with[:limit]
        
        # If not enough, add fuzzy matches
        matches = process.extract(
            partial_upper,
            [str(c).upper() for c in self.package_codes],
            scorer=fuzz.partial_ratio,
            limit=limit * 2
        )
        
        suggestions = starts_with.copy()
        for match_text, score, idx in matches:
            if len(suggestions) >= limit:
                break
            code = self.package_codes[idx]
            if code not in suggestions and score > 70:
                suggestions.append(code)
        
        return suggestions[:limit]


def create_search_engine(data: pd.DataFrame) -> FuzzySearchEngine:
    """
    Convenience function to create search engine
    
    Args:
        data: DataFrame with package data
        
    Returns:
        FuzzySearchEngine instance
    """
    return FuzzySearchEngine(data)


if __name__ == "__main__":
    # Test the search engine
    from data_loader import PackageDataLoader
    
    try:
        # Load data
        loader = PackageDataLoader()
        df = loader.load_data()
        print(f"✅ Loaded {len(df)} packages")
        
        # Create search engine
        search = FuzzySearchEngine(df)
        print("✅ Search engine initialized")
        
        # Test searches
        test_queries = ["D15", "BIG", "game", "ST30"]
        
        for query in test_queries:
            print(f"\n🔍 Searching for: '{query}'")
            results = search.search(query, top_n=5)
            print(f"  Found {len(results)} matches:")
            for i, pkg in enumerate(results, 1):
                score = pkg.get('_similarity_score', 0)
                print(f"    {i}. {pkg['package_code']} - {pkg['package_name']} "
                      f"(Score: {score:.1f})")
        
        # Test exact match
        print(f"\n🎯 Exact match for 'D15':")
        exact = search.exact_match("D15")
        if exact:
            print(f"  ✅ Found: {exact['package_code']} - "
                  f"Price: {exact['price']:,.0f} VNĐ")
        
        # Test suggestions
        print(f"\n💡 Suggestions for 'D':")
        suggestions = search.get_suggestions("D", limit=5)
        print(f"  {', '.join(suggestions)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
