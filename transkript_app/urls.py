from django.urls import path

from .views import check_transcript, home_page, all_create_view

urlpatterns = [
    path('', home_page, name='home_page'),
    path('checkdocuments/transcript/<int:student_id>/', check_transcript, name='check_transcript'),

    # All create
    path('transkript/all-create/', all_create_view, name='all_create_transkript'),
]
