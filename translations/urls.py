from django.contrib import admin
from django.urls import path

from .views import import_aya_from_csv, import_sura_from_json

urlpatterns = [
    path('import/sura', import_sura_from_json),
    path('import/aya', import_aya_from_csv),
]
