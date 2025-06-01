from django.shortcuts import get_object_or_404, redirect
from django.http import Http404, FileResponse, HttpResponse

# All create
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
import pandas as pd

from .models import Transkript, Fakultet, Yonalish, OqishTuri, OqishKursi, OqishTili
from django.core.files.uploadedfile import InMemoryUploadedFile


def home_page(request):
    # return HttpResponse("Hello")
    return redirect('https://auezov.edu.kz/')

def check_transcript(request, student_id):
    transcript = get_object_or_404(Transkript, student_id=student_id)

    if not transcript.transkript_pdf:
        raise Http404("Transkript PDF topilmadi")

    return FileResponse(transcript.transkript_pdf.open('rb'), filename=f"{transcript.transkript_pdf}")


def latin_to_russian_alifbo(text):
    mapping = {
        "sh": "ш", "ch": "ч", "ya": "я", "yo": "ё", "yu": "ю",
        "ts": "ц", "ng": "нг",
        "o‘": "у", "o'": "у", "o`": "у",
        "g‘": "г", "g'": "г", "g`": "г",
        "a": "а", "b": "б", "d": "д", "e": "е", "f": "ф", "g": "г",
        "h": "х", "i": "и", "j": "ж", "k": "к", "l": "л", "m": "м",
        "n": "н", "o": "о", "p": "п", "q": "к", "r": "р", "s": "с",
        "t": "т", "u": "у", "v": "в", "x": "кс", "y": "й", "z": "з",
        "'": "", "`": "", "ʼ": "", "’": "", " ": " ",
    }

    complex = ["sh", "ch", "ng", "ya", "yo", "yu", "ts", "o‘", "o'", "o`", "g‘", "g'", "g`"]

    text = text.lower()
    result = ""
    i = 0
    while i < len(text):
        matched = False
        for c in complex:
            if text[i:i+len(c)] == c:
                result += mapping[c]
                i += len(c)
                matched = True
                break
        if not matched:
            result += mapping.get(text[i], text[i])
            i += 1

    return result



@login_required
@user_passes_test(lambda u: u.is_superuser)
def all_create_view(request):
    fakultetlar = Fakultet.objects.all()
    yonalishlar = Yonalish.objects.all()
    oqish_turlari = OqishTuri.objects.all()
    kurslar = OqishKursi.objects.all()
    tillar = OqishTili.objects.all()

    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file: InMemoryUploadedFile = request.FILES['excel_file']
        created_objects = []
        error_count = 0
        error_rows = []

        try:
            df = pd.read_excel(excel_file)

            fakultet = Fakultet.objects.get(pk=int(request.POST.get('fakultet')))
            yonalish = Yonalish.objects.get(pk=int(request.POST.get('yonalish')))
            oqish_turi = OqishTuri.objects.get(pk=int(request.POST.get('oqish_turi')))
            kurs = OqishKursi.objects.get(pk=int(request.POST.get('kurs')))
            til = OqishTili.objects.get(pk=int(request.POST.get('til')))
            tugatgan_yili = request.POST.get('tugatgan_yili') or "2022"
            year = request.POST.get('year') or "24.08.2022"

            for index, row in df.iterrows():
                try:
                    third = latin_to_russian_alifbo(str(row['passport__third_name']).strip())
                    first = latin_to_russian_alifbo(str(row['passport__first_name']).strip())
                    second = latin_to_russian_alifbo(str(row['passport__second_name']).strip())
                    toliq_ism = f"{third} {first} {second}"

                    obj = Transkript(
                        toliq_ism=toliq_ism,
                        fakultet=fakultet,
                        yonalish=yonalish,
                        oqish_turi=oqish_turi,
                        oqish_kursi=kurs,
                        oqish_tili=til,
                        tugatgan_yili=tugatgan_yili,
                        year=year
                    )
                    created_objects.append(obj)
                except Exception as e:
                    error_count += 1
                    error_rows.append(f"{index + 2} - {e}")

            if created_objects:
                Transkript.objects.bulk_create(created_objects, batch_size=1000)
                messages.success(request, f"✅ {len(created_objects)} транскриптов успешно создано.")
            if error_count:
                messages.error(request, f"❌ В {error_count} строках произошли ошибки.")
                for err in error_rows[:5]:  # показываем только несколько ошибок
                    messages.warning(request, f"⚠️ Строка: {err}")

        except Exception as e:
            messages.error(request, f"❌ Общая ошибка: {str(e)}")

        return redirect('all_create_transkript')

    return render(request, 'all_create.html', {
        'fakultetlar': fakultetlar,
        'yonalishlar': yonalishlar,
        'oqish_turlari': oqish_turlari,
        'kurslar': kurslar,
        'tillar': tillar,
    })
