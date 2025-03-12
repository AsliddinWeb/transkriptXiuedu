from django.contrib import admin
from django.utils.safestring import mark_safe

# History
from simple_history.admin import SimpleHistoryAdmin

# Django unfold
from unfold.admin import ModelAdmin
from .models import Fakultet, Yonalish, OqishTuri, OqishKursi, OqishTili, Transkript, Fan

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
class TranskriptAdmin(ModelAdmin, SimpleHistoryAdmin):
    list_display = ("toliq_ism", "student_id", "fakultet", "yonalish", "oqish_turi", "oqish_kursi", "oqish_tili", "tugatgan_yili", "pdf_link")
    search_fields = ("toliq_ism", "student_id")
    list_filter = ("fakultet", "yonalish", "oqish_turi", "oqish_kursi", "oqish_tili", "tugatgan_yili")

    def pdf_link(self, obj):
        if obj.transkript_pdf:
            return mark_safe(f'<a class="btn btn-blue" href="{obj.transkript_pdf.url}" target="_blank">PDF yuklash</a>')
        return "PDF yo'q"

    pdf_link.short_description = "Transkript PDF"

@admin.register(Fan)
class FanAdmin(ModelAdmin):
    list_display = ("nomi", "yonalish")
    search_fields = ("nomi",)
    list_filter = ("yonalish",)
