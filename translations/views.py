import csv
import json

from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from .models import Sura, Aya


def import_sura_from_json(request):
    with open('/home/sami/quran/sura.json') as f:
        txt = f.read()
        json_data = json.loads(txt)
        tuples_data = []
        for row in json_data:
            obj = {
                'name': row['name'],
                'transliteration_en': row['transliteration_en'],
                'translation_en': row['translation_en'],
                'total_verses': row['total_verses'],
                'revelation_type': row['revelation_type']
            }
            tuples_data.append(Sura(**obj))
        Sura.objects.bulk_create(tuples_data)

    return HttpResponse('done')


def import_aya_from_csv(request):
    with open('/home/sami/quran/aya.csv') as f:
        reader = csv.reader(f)
        tuples_data = []
        for row in reader:
            obj = {
                'sura_id': row[1],
                'aya': row[2],
                'arabic': row[3],
                'ur_maududi': row[4],
                'en_maududi': row[5],
            }
            tuples_data.append(Aya(**obj))

        Aya.objects.bulk_create(tuples_data)

    return HttpResponse('done')


