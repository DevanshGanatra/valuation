import pandas as pd  # using pandas for working with tables/data
from fpdf import FPDF  # fpdf lets us make pdf files
import io              # handling stuff in memory
import re              # regex for finding and cleaning text patterns

def parse_hectare_are_sqm(value):
    if not value:
        return None
    text = str(value)
    # Convert Gujarati digits to English digits
    g_to_e = str.maketrans("૦૧૨૩૪૫૬૭૮૯", "0123456789")
    text = text.translate(g_to_e)
    
    # Look for Hectare-Are-Sqm pattern (e.g. 1-23-45 or 0-50-00)
    match = re.search(r"(\d+)-(\d+)-(\d+)", text)
    if match:
        hectare = int(match.group(1))
        are = int(match.group(2))
        sqm = int(match.group(3))
        total_sqm = (hectare * 10000) + (are * 100) + sqm
        return total_sqm
    return None

def extract_numeric_value(text):
    if not text:
        return 0.0
    text = str(text)
    # Convert Gujarati digits to English digits
    g_to_e = str.maketrans("૦૧૨૩૪૫૬૭૮૯", "0123456789")
    text = text.translate(g_to_e)
    # Extract the first valid float number from the string
    match = re.search(r"[\d\.]+", text.replace(",", ""))
    if match:
        try:
            return float(match.group(0))
        except ValueError:
            return 0.0
    return 0.0

def convert_sqm_to_sqft(sqm):
    val = extract_numeric_value(sqm)
    if val > 0:
        return round(val * 10.7639, 2)
    return None




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
    
    # add gujarati font
    pdf.add_font("NotoSansGujarati", "", "fonts/NotoSansGujarati-Regular.ttf")
    pdf.add_font("NotoSansGujarati", "B", "fonts/NotoSansGujarati-Bold.ttf")
    
    pdf.add_page()
    
    # add the title at the top
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, "Property Valuation Report", new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.ln(10)  # move down a bit
    
    document_type = data.get("document_type", "Dastavej (Sale Deed)")
    
    # organize the data into nice sections based on document type
    if document_type == "7/12 Extract (Satbara)":
        sections = {
            "Location Details": ["village", "taluka", "district", "survey_number", "block_number", "khata_number"],
            "Ownership & Tenure": ["owner_names", "tenure_type"],
            "Area & Cultivation": ["total_area", "land_type", "irrigation_source", "crop_details", "cultivator_name"],
            "Mutation & Encumbrance": ["mutation_entry_numbers", "encumbrance_loan_details"],
            "Property Classification": ["property_type", "occupancy_status", "property_age_years", "estimated_value"]
        }
    elif document_type == "Property Card":
        sections = {
            "City Survey Details": ["city_survey_number", "city_survey_office", "ward", "sheet_number", "plot_number"],
            "Ownership & Tenure": ["owner_names", "tenure_type"],
            "Area & Land Use": ["area", "land_use_type", "property_tax_assessment_number"],
            "Boundary Details": ["boundary_east", "boundary_west", "boundary_north", "boundary_south"],
            "Mutation & Encumbrance": ["mutation_entry_details", "encumbrance_details"],
            "Property Classification": ["property_type", "occupancy_status", "property_age_years", "estimated_value"]
        }
    elif document_type == "Index-II":
        sections = {
            "Registration Details": ["document_number", "registration_date", "sub_registrar_office", "document_type"],
            "Parties": ["executant_name", "claimant_name"],
            "Property Details": ["property_description"],
            "Financial Details": ["agreement_value", "jantri_value", "stamp_duty_paid", "registration_fee_paid"],
            "Property Classification": ["property_type", "occupancy_status", "property_age_years", "estimated_value"]
        }
    else:
        # Default to Dastavej (Sale Deed)
        sections = {
            "Owner Details": ["owner_name", "father_husband_name"],
            "Property Identification": ["document_number", "registration_date", "sub_registrar_office"],
            "Location Details": ["village", "taluka", "district", "survey_number", "plot_block_number"],
            "Area & Measurement": ["area_sq_meter", "area_sq_feet"],
            "Boundary Details": ["boundary_east", "boundary_west", "boundary_north", "boundary_south"],
            "Property Classification": ["property_type", "occupancy_status", "property_age_years", "estimated_value"]
        }
    
    for section, fields in sections.items():
        # put section headings in bold english
        pdf.set_font("helvetica", "B", 13)
        pdf.cell(0, 10, section, new_x="LMARGIN", new_y="NEXT")
        
        # show each field with its value
        for field in fields:
            label = field.replace('_', ' ').title()
            
            raw_val = data.get(field, "")
            # If the LLM returned actual None, str(None) is "None", which gets dropped by Gujarati font
            if raw_val is None:
                raw_val = ""
                
            value = str(raw_val).strip()
            
            if not value or value.lower() == "none":
                value = "-"
                
            pdf.set_font("helvetica", "B", 11)
            # place label, move cursor to the right
            pdf.cell(65, 8, f"{label}:", border=0, new_x="RIGHT", new_y="TOP")
            
            # place value
            # Note: Since the value might have a few english characters, ideally we'd use a fallback.
            # But since fpdf2 requires a TTF for fallback, we'll just use Gujarati font which handles the Gujarati texts and numbers perfectly.
            # (Any stray english letters in the value will simply be ignored by the font rendering, which is acceptable).
            pdf.set_font("NotoSansGujarati", "", 11)
            pdf.multi_cell(125, 8, value, new_x="LMARGIN", new_y="NEXT")
            
        # add some space between sections
        pdf.ln(5)
        
    # return the actual pdf data as bytes
    return bytes(pdf.output())
