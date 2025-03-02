from django.contrib import admin

# Django unfold
from unfold.admin import ModelAdmin
from .models import Fakultet, Yonalish, OqishTuri, OqishKursi, OqishTili, Transkript

@admin.register(Fakultet)
class FakultetAdmin(ModelAdmin):
    list_display = ("nomi",)
    search_fields = ("nomi",)

@admin.register(Yonalish)
class YonalishAdmin(ModelAdmin):
    list_display = ("nomi", "kodi")
    search_fields = ("nomi", "kodi")

@admin.register(OqishTuri)
class OqishTuriAdmin(ModelAdmin):
    list_display = ("nomi",)
    search_fields = ("nomi",)

@admin.register(OqishKursi)
class OqishKursiAdmin(ModelAdmin):
    list_display = ("nomi",)
    search_fields = ("nomi",)

@admin.register(OqishTili)
class OqishTiliAdmin(ModelAdmin):
    list_display = ("nomi",)
    search_fields = ("nomi",)

@admin.register(Transkript)
class TranskriptAdmin(ModelAdmin):
    list_display = ("toliq_ism", "student_id", "fakultet", "yonalish", "oqish_turi", "oqish_kursi", "oqish_tili", "tugatgan_yili")
    search_fields = ("toliq_ism", "student_id")
    list_filter = ("fakultet", "yonalish", "oqish_turi", "oqish_kursi", "oqish_tili", "tugatgan_yili")

