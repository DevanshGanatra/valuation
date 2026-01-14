import pandas as pd
from fpdf import FPDF
import io

def convert_sqm_to_sqft(sqm):
    try:
        if sqm and str(sqm).replace('.', '', 1).isdigit():
            return round(float(sqm) * 10.7639, 2)
    except:
        pass
    return None

def generate_excel(data):
    """Generates an Excel file in memory."""
    df = pd.DataFrame([data])
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Valuation Data')
    return output.getvalue()

def generate_pdf_report(data):
    """Generates a PDF report using fpdf2."""
    pdf = FPDF()
    pdf.add_page()
    
    # Set title
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Property Valuation Report", ln=True, align='C')
    pdf.ln(10)
    
    # Set content
    pdf.set_font("Helvetica", size=12)
    
    sections = {
        "Owner Details": ["owner_name", "father_husband_name"],
        "Property Identification": ["document_number", "registration_date", "sub_registrar_office"],
        "Location Details": ["village", "taluka", "district", "survey_number", "plot_block_number"],
        "Area & Measurement": ["area_sq_meter", "area_sq_feet"],
        "Boundary Details": ["boundary_east", "boundary_west", "boundary_north", "boundary_south"]
    }
    
    for section, fields in sections.items():
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 10, section, ln=True)
        pdf.set_font("Helvetica", size=11)
        for field in fields:
            label = field.replace('_', ' ').title()
            value = str(data.get(field, ''))
            pdf.cell(50, 8, f"{label}:", border=0)
            # Handle potential unicode issues in fpdf (Gujarati might not render without font embedding)
            # For now, we will use English labels and values. 
            # Note: To support Gujarati in PDF, we need a TTF/OTF font file.
            pdf.multi_cell(0, 8, value)
        pdf.ln(5)
        
    return pdf.output()
