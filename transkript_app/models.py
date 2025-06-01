from django.db import models

import random

from simple_history.models import HistoricalRecords

class Fakultet(models.Model):
    nomi = models.CharField(max_length=255, verbose_name="Fakultet nomi")

    def __str__(self):
        return self.nomi

    class Meta:
        verbose_name = "Fakultet"
        verbose_name_plural = "Fakultetlar"

class Yonalish(models.Model):
    nomi = models.CharField(max_length=255, verbose_name="Yo'nalish nomi")
    kodi = models.CharField(max_length=255, verbose_name="Yo'nalish kodi")
    shablon_docx = models.FileField(upload_to='shablons/', verbose_name="Shablon DOCX", null=True, blank=True)

    def __str__(self):
        return f"{self.nomi} - {self.kodi}"

    class Meta:
        verbose_name = "Yo'nalish"
        verbose_name_plural = "Yo'nalishlar"

class OqishTuri(models.Model):
    nomi = models.CharField(max_length=255, verbose_name="O'qish turi")

    def __str__(self):
        return self.nomi

    class Meta:
        verbose_name = "O'qish turi"
        verbose_name_plural = "O'qish turlari"

class OqishKursi(models.Model):
    nomi = models.CharField(max_length=255, verbose_name="O'qish kursi")

    def __str__(self):
        return self.nomi

    class Meta:
        verbose_name = "O'qish kursi"
        verbose_name_plural = "O'qish kurslari"

class OqishTili(models.Model):
    nomi = models.CharField(max_length=255, verbose_name="O'qish tili")

    def __str__(self):
        return self.nomi

    class Meta:
        verbose_name = "O'qish tili"
        verbose_name_plural = "O'qish tillari"

class Transkript(models.Model):
    toliq_ism = models.CharField(max_length=255, verbose_name="To'liq ismi")
    fakultet = models.ForeignKey(Fakultet, on_delete=models.CASCADE, verbose_name="Fakultet")
    yonalish = models.ForeignKey(Yonalish, on_delete=models.CASCADE, verbose_name="Yo'nalish")

    oqish_turi = models.ForeignKey(OqishTuri, on_delete=models.CASCADE, verbose_name="O'qish turi")
    oqish_kursi = models.ForeignKey(OqishKursi, on_delete=models.CASCADE, verbose_name="O'qish kursi")
    oqish_tili = models.ForeignKey(OqishTili, on_delete=models.CASCADE, verbose_name="O'qish tili")
    tugatgan_yili = models.CharField(max_length=255, default="2022", verbose_name="O'qishga kirgan yili")
    student_id = models.IntegerField(verbose_name="Student ID", unique=True, blank=True, null=True)
    year = models.CharField(max_length=255, default="24.08.2022")

    transkript_pdf = models.FileField(null=True, blank=True, verbose_name="Transkript PDF")

    history = HistoricalRecords()

    def __str__(self):
        return self.toliq_ism

    def generate_unique_student_id(self):
        """ 6 xonali unikal student ID generatsiya qilish """
        while True:
            new_id = random.randint(100000, 999999)  # 6 xonali tasodifiy son yaratish
            if not Transkript.objects.filter(student_id=new_id).exists():
                return new_id

    def save(self, *args, **kwargs):
        """ Saqlashdan oldin student_id avtomatik ravishda yaratish """
        if not self.student_id:
            self.student_id = self.generate_unique_student_id()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Transkript"
        verbose_name_plural = "Transkriptlar"

class Fan(models.Model):
    yonalish = models.ForeignKey(Yonalish, verbose_name="Yo'nalish", on_delete=models.CASCADE, related_name="fanlar")
    nomi = models.CharField(max_length=255, verbose_name="Fan nomi")

    def __str__(self):
        return self.nomi

    class Meta:
        verbose_name = "Fan"
        verbose_name_plural = "Fanlar"
