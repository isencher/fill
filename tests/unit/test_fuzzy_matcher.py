"""
Unit tests for Fuzzy Matcher service.
"""

import pytest
from src.services.fuzzy_matcher import FuzzyMatcher, suggest_column_mappings


class TestFuzzyMatcherSimilarity:
    """Test string similarity calculation."""

    def test_exact_match_returns_one(self):
        """Exact match should return 1.0."""
        matcher = FuzzyMatcher()
        assert matcher.calculate_similarity("客户名称", "客户名称") == 1.0
        assert matcher.calculate_similarity("Amount", "amount") == 1.0

    def test_completely_different_returns_low(self):
        """Completely different strings should return low score."""
        matcher = FuzzyMatcher()
        score = matcher.calculate_similarity("abc", "xyz")
        assert score < 0.3

    def test_similar_strings_return_high_score(self):
        """Similar strings should return high score."""
        matcher = FuzzyMatcher()
        score = matcher.calculate_similarity("客户名称", "客户姓名")
        assert score > 0.5

    def test_empty_strings_return_zero(self):
        """Empty strings should return 0."""
        matcher = FuzzyMatcher()
        assert matcher.calculate_similarity("", "test") == 0.0
        assert matcher.calculate_similarity("test", "") == 0.0


class TestFuzzyMatcherSynonyms:
    """Test synonym matching."""

    def test_synonym_names_match(self):
        """Name synonyms should match."""
        matcher = FuzzyMatcher()
        score = matcher.check_synonym_match("名称", "姓名")
        assert score == 0.95

    def test_synonym_amount_match(self):
        """Amount synonyms should match."""
        matcher = FuzzyMatcher()
        score = matcher.check_synonym_match("金额", "价格")
        assert score == 0.95

    def test_synonym_date_match(self):
        """Date synonyms should match."""
        matcher = FuzzyMatcher()
        score = matcher.check_synonym_match("日期", "时间")
        assert score == 0.95

    def test_non_synonyms_return_zero(self):
        """Non-synonyms should return 0."""
        matcher = FuzzyMatcher()
        score = matcher.check_synonym_match("颜色", "金额")
        assert score == 0.0


class TestFuzzyMatcherBestMatch:
    """Test best match finding."""

    def test_find_exact_match(self):
        """Should find exact match."""
        matcher = FuzzyMatcher()
        columns = ["客户名称", "金额", "日期"]
        match, score = matcher.find_best_match("金额", columns)
        
        assert match == "金额"
        assert score == 1.0

    def test_find_similar_match(self):
        """Should find similar match."""
        matcher = FuzzyMatcher()
        columns = ["客户姓名", "总价", "开票日期"]
        match, score = matcher.find_best_match("金额", columns)
        
        assert match == "总价"
        assert score > 0.7

    def test_no_candidates_returns_none(self):
        """Empty candidates should return None."""
        matcher = FuzzyMatcher()
        match, score = matcher.find_best_match("test", [])
        
        assert match is None
        assert score == 0.0


class TestFuzzyMatcherSuggestMappings:
    """Test mapping suggestion."""

    def test_suggest_mappings_returns_all_placeholders(self):
        """Should return suggestion for each placeholder."""
        matcher = FuzzyMatcher()
        placeholders = ["客户", "金额"]
        columns = ["客户名称", "总价", "日期"]
        
        suggestions = matcher.suggest_mappings(placeholders, columns)
        
        assert len(suggestions) == 2
        assert all("placeholder" in s for s in suggestions)
        assert all("confidence" in s for s in suggestions)

    def test_high_confidence_for_exact_match(self):
        """Exact match should have high confidence."""
        matcher = FuzzyMatcher()
        placeholders = ["金额"]
        columns = ["金额", "日期"]
        
        suggestions = matcher.suggest_mappings(placeholders, columns)
        
        assert suggestions[0]["level"] == "high"
        assert suggestions[0]["confidence"] == 1.0

    def test_medium_confidence_for_similar(self):
        """Similar match should have medium confidence."""
        matcher = FuzzyMatcher(threshold_high=0.95, threshold_medium=0.6)
        placeholders = ["金额"]  # Synonym of "总价"
        columns = ["客户", "总价"]
        
        suggestions = matcher.suggest_mappings(placeholders, columns)
        
        # "金额" and "总价" are synonyms, should be high or medium
        assert suggestions[0]["level"] in ["medium", "high"]


class TestConvenienceFunction:
    """Test convenience function."""

    def test_suggest_column_mappings_returns_tuple(self):
        """Should return tuple of suggestions and confidence."""
        placeholders = ["客户", "金额"]
        columns = ["客户名称", "总价"]
        
        suggestions, confidence = suggest_column_mappings(placeholders, columns)
        
        assert isinstance(suggestions, list)
        assert isinstance(confidence, float)
        assert 0 <= confidence <= 1

    def test_overall_confidence_calculation(self):
        """Overall confidence should be average of individual scores."""
        placeholders = ["金额", "日期"]
        columns = ["金额", "日期"]  # Exact matches
        
        suggestions, confidence = suggest_column_mappings(placeholders, columns)
        
        assert confidence == 1.0


class TestFuzzyMatcherNormalization:
    """Test text normalization."""

    def test_normalize_removes_suffix(self):
        """Normalization should extract core meaning."""
        matcher = FuzzyMatcher()
        
        # Should recognize "客户名称" and "名称" as related
        result1 = matcher.normalize("客户名称")
        result2 = matcher.normalize("供应商名称")
        
        assert result1 == result2 == "名称"

    def test_normalize_handles_whitespace(self):
        """Should handle whitespace."""
        matcher = FuzzyMatcher()
        result = matcher.normalize("  金额  ")
        
        assert result == "金额"
