import pandas as pd  # using pandas for working with tables/data
from fpdf import FPDF  # fpdf lets us make pdf files
import io              # handling stuff in memory
import re              # regex for finding and cleaning text patterns

def convert_sqm_to_sqft(sqm):
    # just multipling by 10.7639
    try:
        if sqm is None:
            return None
        # cleaning it up, remove spaces and commas
        normalized = str(sqm).strip()
        if not normalized:
            return None
        normalized = normalized.replace(",", "")
        normalized = re.sub(r"\s+", "", normalized)
        # make sure its actually a number before doing math
        if normalized.replace(".", "", 1).isdigit():
            return round(float(normalized) * 10.7639, 2)
    except Exception:
        #  went wrong then return none
        return None
    return None


def _safe_pdf_text(value):
    # makes sure pdfs dont break with weird characters
    # just replace stuff pdfs dont like with a question mark
    text = str(value or "")
    return text.encode("latin-1", errors="replace").decode("latin-1")

def generate_excel(data):
    # making an excel file from the data
    # turn the data into a table
    df = pd.DataFrame([data])
    # make a virtual file in memory
    output = io.BytesIO()
    # save it as excel
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Valuation Data')
    # return the actual file data
    return output.getvalue()

def generate_pdf_report(data):
    # making a nice pdf report from the property data
    pdf = FPDF()
    pdf.add_page()
    
    # add the title at the top
    pdf.set_font("Helvetica", "B", 16)  # b is bold
    pdf.cell(0, 10, "Property Valuation Report", ln=True, align='C')
    pdf.ln(10)  # move down a bit
    
    # set up the text for the content
    pdf.set_font("Helvetica", size=12)
    
    # organize the data into nice sections
    sections = {
        "Owner Details": ["owner_name", "father_husband_name"],
        "Property Identification": ["document_number", "registration_date", "sub_registrar_office"],
        "Location Details": ["village", "taluka", "district", "survey_number", "plot_block_number"],
        "Area & Measurement": ["area_sq_meter", "area_sq_feet"],
        "Boundary Details": ["boundary_east", "boundary_west", "boundary_north", "boundary_south"]
    }
    
    for section, fields in sections.items():
        # put section headings in bold
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 10, section, ln=True)
        
        # show each field with its value
        pdf.set_font("Helvetica", size=11)
        for field in fields:
            # convert owner_name to Owner Name format
            label = field.replace('_', ' ').title()
            value = _safe_pdf_text(data.get(field, ""))
            # put the label
            pdf.cell(50, 8, f"{label}:", border=0)
            # put the value (multi_cell wraps long text)
            pdf.multi_cell(0, 8, value)
        # add some space between sections
        pdf.ln(5)
        
    # return the actual pdf data
    return pdf.output()
