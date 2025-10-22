from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import AnalyzedString
from .serializers import AnalyzedStringSerializer
from .utils import analyze_string
import re

class StringListCreateView(APIView):
    def post(self, request):
        value = request.data.get("value")

        if value is None:
            return Response({"error": "Missing 'value' field"}, status=status.HTTP_400_BAD_REQUEST)
        if not isinstance(value, str):
            return Response({"error": "'value' must be a string"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        analyzed = analyze_string(value)

        if AnalyzedString.objects.filter(id=analyzed["id"]).exists():
            return Response({"error": "String already exists"}, status=status.HTTP_409_CONFLICT)

        obj = AnalyzedString.objects.create(
            id=analyzed["id"],
            value=analyzed["value"],
            length=analyzed["length"],
            is_palindrome=analyzed["is_palindrome"],
            unique_characters=analyzed["unique_characters"],
            word_count=analyzed["word_count"],
            character_frequency_map=analyzed["character_frequency_map"],
        )

        serializer = AnalyzedStringSerializer(obj)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request):
        strings = AnalyzedString.objects.all()
        filters_applied = {}

        is_palindrome = request.query_params.get("is_palindrome")
        min_length = request.query_params.get("min_length")
        max_length = request.query_params.get("max_length")
        word_count = request.query_params.get("word_count")
        contains_character = request.query_params.get("contains_character")

        try:
            if is_palindrome is not None:
                val = is_palindrome.lower() == "true"
                strings = strings.filter(is_palindrome=val)
                filters_applied["is_palindrome"] = val
            if min_length:
                strings = strings.filter(length__gte=int(min_length))
                filters_applied["min_length"] = int(min_length)
            if max_length:
                strings = strings.filter(length__lte=int(max_length))
                filters_applied["max_length"] = int(max_length)
            if word_count:
                strings = strings.filter(word_count=int(word_count))
                filters_applied["word_count"] = int(word_count)
            if contains_character:
                strings = strings.filter(value__icontains=contains_character)
                filters_applied["contains_character"] = contains_character
        except ValueError:
            return Response({"error": "Invalid query parameter value"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = AnalyzedStringSerializer(strings, many=True)
        return Response({
            "data": serializer.data,
            "count": strings.count(),
            "filters_applied": filters_applied
        }, status=status.HTTP_200_OK)


class StringDetailView(APIView):
    def get(self, request, string_value):
        try:
            obj = AnalyzedString.objects.get(value=string_value)
        except AnalyzedString.DoesNotExist:
            return Response({"error": "String not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = AnalyzedStringSerializer(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, string_value):
        try:
            obj = AnalyzedString.objects.get(value=string_value)
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except AnalyzedString.DoesNotExist:
            return Response({"error": "String not found"}, status=status.HTTP_404_NOT_FOUND)


class NaturalLanguageFilterView(APIView):
    def get(self, request):
        query = request.query_params.get("query")
        if not query:
            return Response({"error": "Missing query parameter"}, status=status.HTTP_400_BAD_REQUEST)

        filters = {}
        q = AnalyzedString.objects.all()

        text = query.lower()

        if "palindromic" in text or "palindrome" in text:
            filters["is_palindrome"] = True
            q = q.filter(is_palindrome=True)
        if "single word" in text or "one word" in text:
            filters["word_count"] = 1
            q = q.filter(word_count=1)
        match = re.search(r"longer than (\\d+)", text)
        if match:
            min_len = int(match.group(1)) + 1
            filters["min_length"] = min_len
            q = q.filter(length__gte=min_len)
        match = re.search(r"containing the letter ([a-z])", text)
        if match:
            ch = match.group(1)
            filters["contains_character"] = ch
            q = q.filter(value__icontains=ch)

        if not filters:
            return Response({"error": "Unable to parse natural language query"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = AnalyzedStringSerializer(q, many=True)
        return Response({
            "data": serializer.data,
            "count": q.count(),
            "interpreted_query": {
                "original": query,
                "parsed_filters": filters
            }
        }, status=status.HTTP_200_OK)
