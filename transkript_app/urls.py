from django.urls import path

from .views import check_transcript, home_page

urlpatterns = [
    path('', home_page, name='home_page'),
    path('checkdocuments/transcript/<int:student_id>/', check_transcript, name='check_transcript'),
]
