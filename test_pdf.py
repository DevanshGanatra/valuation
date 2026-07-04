import utils
import os

data = {
    "owner_name": "દેવાંશ ગણાત્રા",
    "father_husband_name": "જયેશભાઈ",
    "document_number": "12345",
    "registration_date": "04-07-2026",
    "sub_registrar_office": "અમદાવાદ",
    "village": "પાલડી",
    "taluka": "અમદાવાદ શહેર",
    "district": "અમદાવાદ",
    "survey_number": "૭૮૯",
    "plot_block_number": "બી-૧૨",
    "area_sq_meter": "100",
    "area_sq_feet": "1076.39",
    "boundary_east": "પૂર્વ દિશાનો પ્લોટ",
    "boundary_west": "પશ્ચિમ દિશાનો રસ્તો",
    "boundary_north": "ઉત્તર દિશા",
    "boundary_south": "દક્ષિણ દિશા"
}

pdf_bytes = utils.generate_pdf_report(data)
with open("test_gujarati_report.pdf", "wb") as f:
    f.write(pdf_bytes)

print("PDF generated successfully and saved to test_gujarati_report.pdf")
