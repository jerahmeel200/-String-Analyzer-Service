from django.urls import path
from .views import StringListCreateView, StringDetailView, NaturalLanguageFilterView

urlpatterns = [
    path('strings', StringListCreateView.as_view()),
    path('strings/<str:string_value>', StringDetailView.as_view()),
    path('strings/filter-by-natural-language', NaturalLanguageFilterView.as_view()),
]
