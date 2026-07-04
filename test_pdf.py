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

data_712 = {
    "document_type": "7/12 Extract (Satbara)",
    "village": "પાલડી",
    "taluka": "અમદાવાદ શહેર",
    "district": "અમદાવાદ",
    "survey_number": "૧૨૩",
    "block_number": "૪૫",
    "khata_number": "૬૭૮",
    "owner_names": "દેવાંશ ગણાત્રા",
    "tenure_type": "જૂની શરત",
    "total_area": "1-23-45",
    "land_type": "ખેતીલાયક",
    "irrigation_source": "કુવો",
    "crop_details": "ઘઉં, કપાસ",
    "cultivator_name": "-",
    "mutation_entry_numbers": "૧૦૦૧, ૧૦૦૨",
    "encumbrance_loan_details": "બેંક ઓફ બરોડા લોન",
    "rate_per_sqft": 1500,
    "property_age_years": 10,
    "estimated_value": "₹ 1,500,000.00"
}

pdf_bytes_712 = utils.generate_pdf_report(data_712)
with open("test_712_report.pdf", "wb") as f:
    f.write(pdf_bytes_712)

print("7/12 PDF generated successfully and saved to test_712_report.pdf")
