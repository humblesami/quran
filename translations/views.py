import csv
import json
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import ListView, DetailView

from django.conf import settings
from .models import Sura, Aya


class MetaInfo:
    @staticmethod
    def get_meta(title='', keywords='', description=''):
        default_des = "Watch 92news hd headlines, breaking news and programs | Muqabil, Cross Talk, Hard Talk Pakistan"
        default_des +=", Ho kya Raha Hai, Night Edition, Subh-e-noor, Subh-saveray-pkaistan, 92-at-8 "
        description = description or default_des
        meta_info = {
            "title": title or "92news hd tv channel headlines, breaking news and programs",
            "keywords": keywords or """
            92 News Videos and Programs Muqabil, Cross Talk, Hard Talk Pakistan Ho kya Raha Hai,
            Night Edition, Subh-e-noor, Subh-saveray-pkaistan, 92-at-8, Pakistan
            """,
            "description": description
        }
        return meta_info


class HomePageView(ListView):
    # paginate_by = 20
    queryset = Sura.objects.all()
    template_name = 'category_list.html'

    def get_context_data(self, **kwargs):
        next = self.request.GET.get('next')
        prev = self.request.GET.get('prev')
        context = super().get_context_data(**kwargs)
        context['meta_info'] = MetaInfo.get_meta()
        return context


class SuraDetailView(DetailView):
    template_name = 'category_details.html'
    model = Sura

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ayas = list(context['object'].ayas.all().values())
        context['ayas'] = ayas
        return context


def search_quran(request, kw=None):
    if not kw:
        kw = request.GET.get('kw')
    if not kw:
        qs = []
    else:
        qs = Aya.objects.filter(plain__icontains=kw)
        qs = qs.order_by('sura','aya')
    ctx = {'results': qs, 'search_kw': kw, 'count': qs.count()}
    res = render(request, 'search_quran_results.html', ctx)
    return res


def import_sura_from_json(request):
    if Sura.objects.all().count():
        return HttpResponse('Already done')
    file_name = '/home/sami/quran/sura.json'
    file_name = 'sura.json'
    file_path = str(settings.BASE_DIR) + '/' + file_name
    with open(file_path) as f:
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
    if not Sura.objects.all().count():
        import_sura_from_json(request)
    if Aya.objects.all().count():
        return HttpResponse('Already done')
    file_name = '/home/sami/quran/quran_text.csv'
    file_name = 'quran_text.csv'
    file_path = str(settings.BASE_DIR) + '/' + file_name
    with open(file_path) as f:
        reader = csv.reader(f)
        tuples_data = []
        for row in reader:
            obj = {
                'sura_id': row[1],
                'aya': row[2],
                'arabic': row[3],
                'plain': row[4],
                'ur_maududi': row[5],
                'en_maududi': row[6],
            }
            tuples_data.append(Aya(**obj))

        Aya.objects.bulk_create(tuples_data)
    return HttpResponse('done')
