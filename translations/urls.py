from django.contrib import admin
from django.urls import path

from .views import search_quran, HomePageView, SuraDetailView, import_aya_from_csv, import_sura_from_json

urlpatterns = [
    path('search/', search_quran),
    path('search/<kw>/', search_quran),
    path('sura/', HomePageView.as_view()),
    path('sura/<pk>/', SuraDetailView.as_view()),
    path('import/sura/', import_sura_from_json),
    path('import/aya/', import_aya_from_csv),
]
