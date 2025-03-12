from django.db.models.signals import post_save
from django.dispatch import receiver

import os
import subprocess
from docx import Document

import tempfile
from django.core.files import File

from docx.shared import Pt, Inches
from docx.oxml.ns import qn

# Env
from dotenv import load_dotenv

# loading env
load_dotenv()

# QR Code
import qrcode
from io import BytesIO


from .models import Transkript


@receiver(post_save, sender=Transkript)
def generate_transkript_pdf(sender, instance, created, **kwargs):
    try:
        doc = Document(instance.yonalish.shablon_docx.path)

        # QR Code

        base_url = "http://192.168.2.109:8000" if os.getenv("DJANGO_ENV") == "dev" else "https://as.uz"


        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=2,
            border=3,
        )
        qr.add_data(f"{base_url}/checkdocuments/transcript/{instance.student_id}/")
        qr.make(fit=True)

        qr_img = qr.make_image(fill_color="black", back_color="white")

        # QR kodni saqlash uchun vaqtinchalik fayl
        qr_io = BytesIO()
        qr_img.save(qr_io, format='PNG')
        qr_io.seek(0)

        # QR kodni dokumentga qo'shish
        doc.add_picture(qr_io, width=Inches(0.7))
        site_url = doc.add_paragraph(f"{base_url}/checkdocuments/transcript/{instance.student_id}/")
        site_url.style.font.size = Pt(7)
        site_url.style.font.name = 'Calibri'
        site_url.style._element.rPr.rFonts.set(qn('w:eastAsia'), 'Calibri')

        for paragraph in doc.paragraphs:
            print("++++++")
            print(paragraph.text)
            print("++++++")

            replace_text_in_paragraph(paragraph, '{{full_name}}', instance.toliq_ism, 7)

        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        replace_text_in_paragraph(paragraph, '{{full_name}}', instance.toliq_ism, 7)

        for i, table in enumerate(doc.tables):
            print(f"Table {i + 1}:")

            for row in table.rows:
                for cell in row.cells:
                    # Agar cell ichida nested jadval bo'lsa
                    if cell.tables:
                        print("\n  Nested Table Found:")
                        for j, nested_table in enumerate(cell.tables):
                            print(f"  Nested Table {j + 1}:")
                            for nested_row in nested_table.rows:
                                for nested_cell in nested_row.cells:
                                    # print(f"    {nested_cell.text}", end='\t')
                                    # Nested cell ichidagi textni o'zgartirish
                                    for paragraph in nested_cell.paragraphs:
                                        replace_text_in_paragraph(paragraph, '{{table_1_fan_1_baxo}}', "88", 4)
                                print()
                        print()

                    # Oddiy cell ichidagi textni o'zgartirish
                    for paragraph in cell.paragraphs:
                        # replace_text_in_paragraph(paragraph, '{{table_1_fan_1_baxo}}', "88", 4)
                        replace_text_in_paragraph(paragraph, '{{full_name}}', "Asliddin", 7)

                print()
            print("\n" + "=" * 50 + "\n")

        with tempfile.TemporaryDirectory() as temp_dir:

            temp_docx_path = os.path.join(temp_dir, f'transcript_{instance.student_id}.docx')
            doc.save(temp_docx_path)

            temp_pdf_path = os.path.join(temp_dir, f'transcript_{instance.student_id}.pdf')

            try:
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
                            pdf_filename = os.path.splitext(os.path.basename(temp_docx_path))[0] + ".pdf"
                            temp_pdf_path = os.path.join(temp_dir, pdf_filename)
                            break
                    except (subprocess.SubprocessError, FileNotFoundError):
                        continue

                if not success:
                    raise Exception("LibreOffice/OpenOffice dasturini topa olmadik yoki ishga tushira olmadik")

                if os.path.exists(temp_pdf_path):
                    with open(temp_pdf_path, 'rb') as pdf_file:
                        instance.transkript_pdf.save(
                            f'transkript_{instance.student_id}.pdf',
                            File(pdf_file),
                            save=False
                        )

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


def replace_text_in_paragraph(paragraph, placeholder, value, size):
    """
    Paragraf ichidagi placeholder textni almashtirib beradi va Calibri 7 da formatlaydi.
    """
    if placeholder in paragraph.text:
        paragraph.text = paragraph.text.replace(placeholder, str(value))

        for run in paragraph.runs:
            if str(value) in run.text:
                run.font.name = 'Calibri'
                run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Calibri')

                run.font.size = Pt(size)

def remove_table(doc, table_index):
    """
    Word faylidagi berilgan indeksdagi jadvalni o'chiradi.
    """
    tables = doc.tables
    if 0 <= table_index < len(tables):
        tbl = tables[table_index]._element
        tbl.getparent().remove(tbl)
