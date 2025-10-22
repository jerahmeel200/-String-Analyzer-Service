from django_filters import rest_framework as filters
from .models import AnalyzedString
import json

class AnalyzedStringFilter(filters.FilterSet):
    is_palindrome = filters.BooleanFilter(method="filter_is_palindrome")
    min_length = filters.NumberFilter(field_name="properties", method="filter_min_length")
    max_length = filters.NumberFilter(field_name="properties", method="filter_max_length")
    word_count = filters.NumberFilter(method="filter_word_count")
    contains_character = filters.CharFilter(method="filter_contains_character")

    class Meta:
        model = AnalyzedString
        fields = []

    def filter_is_palindrome(self, queryset, name, value):
        return queryset.filter(properties__is_palindrome=value)  # JSON lookup

    def filter_min_length(self, queryset, name, value):
        return queryset.filter(properties__length__gte=value)

    def filter_max_length(self, queryset, name, value):
        return queryset.filter(properties__length__lte=value)

    def filter_word_count(self, queryset, name, value):
        return queryset.filter(properties__word_count=value)

    def filter_contains_character(self, queryset, name, value):
        # For JSONField lookups, check character_frequency_map contains key
        # different DB backends behave differently; fallback to contains lookup in raw JSON string
        from django.db.models import Q
        try:
            # Postgres JSONB operators
            return queryset.filter(properties__character_frequency_map__has_key=value)
        except Exception:
            # fallback: filter where JSON contains the character as key (substring)
            return queryset.filter(Q(properties__contains={ "character_frequency_map": { value: {}}}) | Q(properties__contains={ "character_frequency_map": { value: 0 }} ) )
