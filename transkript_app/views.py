from django.shortcuts import get_object_or_404, redirect
from django.http import Http404, FileResponse, HttpResponse

from .models import Transkript

def home_page(request):
    return HttpResponse("Hello")
    # return redirect('https://auezov.edu.kz/')

def check_transcript(request, student_id):
    transcript = get_object_or_404(Transkript, student_id=student_id)

    if not transcript.transkript_pdf:
        raise Http404("Transkript PDF topilmadi")

    return FileResponse(transcript.transkript_pdf.open('rb'), filename=f"{transcript.transkript_pdf}")
