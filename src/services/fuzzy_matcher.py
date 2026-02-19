"""
Fuzzy Matching Service

Provides intelligent string matching for column-to-placeholder mapping suggestions.
"""

from difflib import SequenceMatcher
from typing import List, Dict, Optional, Tuple


class FuzzyMatcher:
    """
    Fuzzy string matcher for mapping suggestions.
    
    Provides intelligent matching between data columns and template placeholders
    with confidence scoring.
    """
    
    # Common Chinese synonyms for matching
    SYNONYMS = {
        "名称": ["名称", "姓名", "名字", "客户", "用户", "公司", "单位"],
        "姓名": ["姓名", "名称", "名字", "联系人"],
        "日期": ["日期", "时间", "年月日", "日期时间"],
        "金额": ["金额", "价格", "费用", "总价", "合计", "小计", "数值"],
        "数量": ["数量", "数目", "个数", "件数"],
        "地址": ["地址", "位置", "地点", "住址"],
        "电话": ["电话", "手机", "联系方式", "移动电话", "座机"],
    }
    
    def __init__(self, threshold_high: float = 0.9, threshold_medium: float = 0.7):
        """
        Initialize fuzzy matcher.
        
        Args:
            threshold_high: Minimum score for high confidence match
            threshold_medium: Minimum score for medium confidence match
        """
        self.threshold_high = threshold_high
        self.threshold_medium = threshold_medium
    
    def calculate_similarity(self, a: str, b: str) -> float:
        """
        Calculate string similarity between 0 and 1.
        
        Args:
            a: First string
            b: Second string
            
        Returns:
            Similarity score (0-1)
        """
        if not a or not b:
            return 0.0
        
        # Direct match
        if a.lower() == b.lower():
            return 1.0
        
        # Sequence matching
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()
    
    def normalize(self, text: str) -> str:
        """
        Normalize text for matching.
        
        Args:
            text: Input text
            
        Returns:
            Normalized text
        """
        # Remove common suffixes/prefixes and whitespace
        text = text.strip()
        
        # Remove common field suffixes
        suffixes = ["名称", "姓名", "日期", "时间", "金额", "价格", "数量", "地址"]
        for suffix in suffixes:
            if text.endswith(suffix) and len(text) > len(suffix):
                return suffix
        
        return text
    
    def check_synonym_match(self, a: str, b: str) -> float:
        """
        Check if two strings are synonyms.
        
        Args:
            a: First string
            b: Second string
            
        Returns:
            0.95 if synonyms, 0.0 otherwise
        """
        a_normalized = self.normalize(a)
        b_normalized = self.normalize(b)
        
        for category, synonyms in self.SYNONYMS.items():
            a_in_synonyms = any(s in a or a in s for s in synonyms)
            b_in_synonyms = any(s in b or b in s for s in synonyms)
            
            if a_in_synonyms and b_in_synonyms:
                return 0.95
            
            # Direct synonym match
            if a_normalized in synonyms and b_normalized in synonyms:
                return 0.95
        
        return 0.0
    
    def find_best_match(
        self, 
        target: str, 
        candidates: List[str]
    ) -> Tuple[Optional[str], float]:
        """
        Find best matching candidate for target.
        
        Args:
            target: Target string to match
            candidates: List of candidate strings
            
        Returns:
            Tuple of (best_match, score)
        """
        best_match = None
        best_score = 0.0
        
        for candidate in candidates:
            # Calculate base similarity
            score = self.calculate_similarity(target, candidate)
            
            # Check for substring match
            if target.lower() in candidate.lower() or candidate.lower() in target.lower():
                score = max(score, 0.8)
            
            # Check synonyms
            synonym_score = self.check_synonym_match(target, candidate)
            score = max(score, synonym_score)
            
            # Normalize and compare
            norm_target = self.normalize(target)
            norm_candidate = self.normalize(candidate)
            if norm_target and norm_target == norm_candidate:
                score = max(score, 0.9)
            
            if score > best_score:
                best_score = score
                best_match = candidate
        
        return best_match, best_score
    
    def suggest_mappings(
        self, 
        placeholders: List[str], 
        columns: List[str]
    ) -> List[Dict]:
        """
        Suggest mappings between placeholders and columns.
        
        Args:
            placeholders: List of template placeholder names
            columns: List of data column names
            
        Returns:
            List of mapping suggestions with confidence levels
        """
        suggestions = []
        
        for placeholder in placeholders:
            best_match, score = self.find_best_match(placeholder, columns)
            
            # Determine confidence level
            if score >= self.threshold_high:
                level = "high"
            elif score >= self.threshold_medium:
                level = "medium"
            else:
                level = "low"
            
            suggestions.append({
                "placeholder": placeholder,
                "suggested_column": best_match,
                "confidence": round(score, 2),
                "level": level
            })
        
        return suggestions
    
    def calculate_overall_confidence(self, suggestions: List[Dict]) -> float:
        """
        Calculate overall confidence score.
        
        Args:
            suggestions: List of mapping suggestions
            
        Returns:
            Overall confidence (0-1)
        """
        if not suggestions:
            return 0.0
        
        return sum(s["confidence"] for s in suggestions) / len(suggestions)


# Convenience function
def suggest_column_mappings(
    placeholders: List[str], 
    columns: List[str]
) -> Tuple[List[Dict], float]:
    """
    Convenience function to suggest mappings.
    
    Args:
        placeholders: Template placeholder names
        columns: Data column names
        
    Returns:
        Tuple of (suggestions, overall_confidence)
    """
    matcher = FuzzyMatcher()
    suggestions = matcher.suggest_mappings(placeholders, columns)
    confidence = matcher.calculate_overall_confidence(suggestions)
    return suggestions, confidence
