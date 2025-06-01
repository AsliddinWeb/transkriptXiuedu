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
        created_count = 0
        error_count = 0
        error_rows = []

        try:
            df = pd.read_excel(excel_file)

            fakultet_id = int(request.POST.get('fakultet'))
            yonalish_id = int(request.POST.get('yonalish'))
            oqish_turi_id = int(request.POST.get('oqish_turi'))
            kurs_id = int(request.POST.get('kurs'))
            til_id = int(request.POST.get('til'))
            tugatgan_yili = request.POST.get('tugatgan_yili') or "2022"
            year = request.POST.get('year') or "24.08.2022"

            for index, row in df.iterrows():
                try:
                    toliq_ism = f"{row['passport__third_name']} {row['passport__first_name']} {row['passport__second_name']}"
                    transkript = Transkript(
                        toliq_ism=toliq_ism,
                        fakultet=Fakultet.objects.get(pk=fakultet_id),
                        yonalish=Yonalish.objects.get(pk=yonalish_id),
                        oqish_turi=OqishTuri.objects.get(pk=oqish_turi_id),
                        oqish_kursi=OqishKursi.objects.get(pk=kurs_id),
                        oqish_tili=OqishTili.objects.get(pk=til_id),
                        tugatgan_yili=tugatgan_yili,
                        year=year
                    )
                    transkript.save()
                    created_count += 1
                except Exception as e:
                    error_count += 1
                    error_rows.append(f"{index + 2} - {e}")  # 2 chi qator deb qaraladi, header +1

            if created_count:
                messages.success(request, f"✅ {created_count} ta transkript muvaffaqiyatli yaratildi.")
            if error_count:
                messages.error(request, f"❌ {error_count} ta xatolik yuz berdi.")
                for err in error_rows:
                    messages.warning(request, f"⚠️ Qator {err}")

        except Exception as e:
            messages.error(request, f"❌ Umumiy xatolik: {str(e)}")

        return redirect('all_create_transkript')

    return render(request, 'all_create.html', {
        'fakultetlar': fakultetlar,
        'yonalishlar': yonalishlar,
        'oqish_turlari': oqish_turlari,
        'kurslar': kurslar,
        'tillar': tillar,
    })
