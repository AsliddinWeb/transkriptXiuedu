from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
import os
import subprocess
from docx import Document
import tempfile
from django.core.files import File

from docx.shared import Pt
from docx.oxml.ns import qn


from .models import Transkript


@receiver(post_save, sender=Transkript)
def generate_transkript_pdf(sender, instance, created, **kwargs):
    """
    Transkript modeliga ma'lumot qo'shilganda yoki o'zgartirilganda
    shablon.docx fayliga ma'lumotlarni to'ldirib, PDF formatga o'zgartiradi.
    """
    try:
        # To'g'ri yo'lni aniqlaymiz
        base_dir = settings.BASE_DIR
        template_path = os.path.join(base_dir, '../static', 'shablon.docx')

        # Fayl mavjudligini tekshiramiz
        if not os.path.exists(template_path):
            print(f"Xatolik: Shablon fayl topilmadi: {template_path}")
            # Agar fayl topilmasa, boshqa mumkin bo'lgan joylarda izlaymiz
            alternative_paths = [
                os.path.join(base_dir, 'staticfiles', 'shablon.docx'),
                os.path.join(base_dir, 'media', 'shablon.docx'),
                os.path.join(base_dir, 'templates', 'shablon.docx'),
                os.path.join(base_dir, 'shablon.docx')
            ]

            for alt_path in alternative_paths:
                if os.path.exists(alt_path):
                    template_path = alt_path
                    print(f"Shablon fayl topildi: {template_path}")
                    break
            else:
                raise FileNotFoundError(
                    f"Shablon.docx fayli topilmadi. Quyidagi joylarda qidirildi: {[template_path] + alternative_paths}")

        # Shablonni ochish
        doc = Document(template_path)

        # Ma'lumotlarni to'ldirish
        # Placeholder so'zlarni almashtirish
        for paragraph in doc.paragraphs:
            replace_text_in_paragraph(paragraph, '{{toliq_ism}}', instance.toliq_ism)
            replace_text_in_paragraph(paragraph, '{{fakultet}}', instance.fakultet.nomi)
            replace_text_in_paragraph(paragraph, '{{yonalish}}', instance.yonalish.nomi)
            replace_text_in_paragraph(paragraph, '{{yonalish_kodi}}', instance.yonalish.kodi)
            replace_text_in_paragraph(paragraph, '{{oqish_turi}}', instance.oqish_turi.nomi)
            replace_text_in_paragraph(paragraph, '{{oqish_kursi}}', instance.oqish_kursi.nomi)
            replace_text_in_paragraph(paragraph, '{{oqish_tili}}', instance.oqish_tili.nomi)
            replace_text_in_paragraph(paragraph, '{{tugatgan_yili}}', instance.tugatgan_yili)
            replace_text_in_paragraph(paragraph, '{{student_id}}', instance.student_id)

        # Jadval ichidagi matnni almashtirish uchun (agar jadval bo'lsa)
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        replace_text_in_paragraph(paragraph, '{{toliq_ism}}', instance.toliq_ism)
                        replace_text_in_paragraph(paragraph, '{{fakultet}}', instance.fakultet.nomi)
                        replace_text_in_paragraph(paragraph, '{{yonalish}}', instance.yonalish.nomi)
                        replace_text_in_paragraph(paragraph, '{{yonalish_kodi}}', instance.yonalish.kodi)
                        replace_text_in_paragraph(paragraph, '{{oqish_turi}}', instance.oqish_turi.nomi)
                        replace_text_in_paragraph(paragraph, '{{oqish_kursi}}', instance.oqish_kursi.nomi)
                        replace_text_in_paragraph(paragraph, '{{oqish_tili}}', instance.oqish_tili.nomi)
                        replace_text_in_paragraph(paragraph, '{{tugatgan_yili}}', instance.tugatgan_yili)
                        replace_text_in_paragraph(paragraph, '{{student_id}}', instance.student_id)

        # Vaqtinchalik fayllarni saqlash uchun papka
        with tempfile.TemporaryDirectory() as temp_dir:
            # Docx faylni saqlash
            temp_docx_path = os.path.join(temp_dir, f'transkript_{instance.student_id}.docx')
            doc.save(temp_docx_path)

            # Docx faylni PDF ga o'zgartirish (LibreOffice yordamida)
            temp_pdf_path = os.path.join(temp_dir, f'transkript_{instance.student_id}.pdf')

            # LibreOffice CLI chaqirish
            try:
                # Turli operatsion tizimlarda LibreOffice/soffice nomlanishi har xil bo'lishi mumkin
                # Ushbu nomlarni sinab ko'ramiz
                libreoffice_commands = [
                    "libreoffice", "soffice", "openoffice",
                    "/Applications/LibreOffice.app/Contents/MacOS/soffice",  # macOS uchun
                    "C:\\Program Files\\LibreOffice\\program\\soffice.exe",  # Windows uchun
                ]

                success = False
                for cmd in libreoffice_commands:
                    try:
                        result = subprocess.run(
                            [cmd, "--headless", "--convert-to", "pdf", "--outdir", temp_dir, temp_docx_path],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30
                        )
                        if result.returncode == 0:
                            success = True
                            # LibreOffice output faylini aniqlaymiz
                            # (ba'zida chiqish fayl nomi o'zgarishi mumkin)
                            pdf_filename = os.path.splitext(os.path.basename(temp_docx_path))[0] + ".pdf"
                            temp_pdf_path = os.path.join(temp_dir, pdf_filename)
                            break
                    except (subprocess.SubprocessError, FileNotFoundError):
                        continue

                if not success:
                    raise Exception("LibreOffice/OpenOffice dasturini topa olmadik yoki ishga tushira olmadik")

                # PDF faylni modelga saqlash
                if os.path.exists(temp_pdf_path):
                    with open(temp_pdf_path, 'rb') as pdf_file:
                        # transkript_pdf ni yangilash va recursive signal chaqirilishini oldini olish
                        instance.transkript_pdf.save(
                            f'transkript_{instance.student_id}.pdf',
                            File(pdf_file),
                            save=False
                        )

                        # save() funksiyasini post_save signalni qayta ishga tushirmaslik uchun
                        # o'chirib/o'zgartirib qo'yamiz
                        Transkript.objects.filter(id=instance.id).update(
                            transkript_pdf=instance.transkript_pdf.name
                        )
                else:
                    raise FileNotFoundError(f"PDF fayl yaratilmadi: {temp_pdf_path}")

            except Exception as conversion_error:
                print(f"PDF konvertatsiyasida xatolik: {conversion_error}")
                raise

    except Exception as e:
        print(f"Transkript PDF yaratishda xatolik: {e}")
        import traceback
        traceback.print_exc()


def replace_text_in_paragraph(paragraph, placeholder, value):
    """
    Paragraf ichidagi placeholder textni almashtirib beradi va Calibri 7 da formatlaydi.
    """
    if placeholder in paragraph.text:
        # Placeholder ni topish va almashtirish
        paragraph.text = paragraph.text.replace(placeholder, str(value))

        # Yangi matnni formatlash
        for run in paragraph.runs:
            if str(value) in run.text:
                # Fontni Calibri ga o'zgartirish
                run.font.name = 'Calibri'
                run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Calibri')  # East Asian font uchun
                # Font o'lchamini 7 ga o'zgartirish
                run.font.size = Pt(7)
