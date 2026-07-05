import fitz  
import google.generativeai as genai  
import json    
import io     
import re     
from PIL import Image 
import streamlit as st

def get_pdf_images(doc):
    # ok so basically we need to turn each pdf page into an image
    # because the ai needs to see it as a picture to understand whats going on
   
    images = []
    
    # Dynamic resolution scaling: prevent Out-Of-Memory (OOM) crashes on large PDFs
    matrix_scale = 2.0 if len(doc) <= 5 else 1.5 if len(doc) <= 15 else 1.0
    matrix = fitz.Matrix(matrix_scale, matrix_scale)
    
    # Cap processing to first 20 pages to avoid Gemini payload limits and memory spikes
    max_pages = min(len(doc), 20)
    
    for page_num in range(max_pages):
        # grab this specific page
        page = doc.load_page(page_num)
        # turn it in a pixmap thing
        pix = page.get_pixmap(matrix=matrix)  
        # convert it to jpeg bytes (much smaller than png, prevents 503 payload errors)
        img_data = pix.tobytes("jpeg")
        # throw it in our images list
        images.append(Image.open(io.BytesIO(img_data)))
    return images


@st.cache_data(ttl=3600)
def _get_supported_model_candidates(api_key):
   
    preferred = ["gemini-1.5-pro", "gemini-2.0-flash", "gemini-1.5-flash-latest"]
    candidates = []
    try:
        for model in genai.list_models():
            methods = getattr(model, "supported_generation_methods", []) or []
            # only care about models that can generate content 
            if "generateContent" not in methods:
                continue
            name = getattr(model, "name", "")
            if name.startswith("models/"):
                name = name.split("/", 1)[1]
            if "flash" in name:
                candidates.append(name)
    except Exception:
        # if something goes wrong like no internet, just use the backup list
        candidates = []

    # sort based on what we prefer
    ordered = [m for m in preferred if m in candidates]
    remaining = [m for m in candidates if m not in ordered]
    if not ordered and not remaining:
        return preferred
    return ordered + remaining

def extract_structured_data(api_key, pdf_document, document_type="Dastavej (Sale Deed)"):
    # main function 
    genai.configure(api_key=api_key)
    
    #  settings to tell the ai how to behave
    generation_config = {
        "temperature": 0.1,  # low temperature means more precise, less random
        "top_p": 0.95, # we want the ai to consider a wide range of possibilities, not just the most likely ones, because sometimes the most likely guess might be wrong and we want it to have the freedom to give us the correct answer even if it's not the most common one.
        "top_k": 40, # we want the ai to consider the top 40 options for each word it generates, which allows for more creativity and accuracy, especially with specific details in the document.
        "max_output_tokens": 8192,
        "response_mime_type": "application/json",  # make sure ai gives us json back
    }

    # first turning the pdf pages into images
    images = get_pdf_images(pdf_document)
    
    PROMPTS = {
        "Dastavej (Sale Deed)": """
        Analyze the provided images of a Gujarati property document (Dastavej). Read the entire document thoroughly to understand the context properly before extracting.
        Extract the following information and **TRANSLATE ALL VALUES TO ENGLISH**. The final output must be completely in professional English, even if the source is Gujarati.
        If a field is not found, return an empty string or null.
        
        Also include a 'field_confidence' object mapping each field key to "high", "medium", or "low" based on how legible or certain the value was in the source image.
        
        Fields to extract:
        - owner_name (Owner Name: Look specifically for the "Purchaser", "Buyer", or "ખરીદનારા" / ખરીદનાર / વેચાણ લેનાર. This is the true owner.)
        - father_husband_name (Father / Husband Name)
        - survey_number (Survey Number)
        - plot_block_number (Plot / Block Number)
        - village (Village / City)
        - taluka (Taluka)
        - district (District)
        - area_sq_meter (Area in Sq. Meter)
        - area_sq_feet (Area in Sq. Feet)
        - document_number (Document Number)
        - registration_date (Registration Date - DD/MM/YYYY)
        - sub_registrar_office (Sub-Registrar Office)
        - boundary_east (East Boundary: Look for ચતુર્દિશા or ચતુર્સીમા / East / પૂર્વ)
        - boundary_west (West Boundary: Look for ચતુર્દિશા or ચતુર્સીમા / West / પશ્ચિમ)
        - boundary_north (North Boundary: Look for ચતુર્દિશા or ચતુર્સીમા / North / ઉત્તર)
        - boundary_south (South Boundary: Look for ચતુર્દિશા or ચતુર્સીમા / South / દક્ષિણ)
        - property_type (Property Type: Is it Land, Flat, Shop, Rowhouse, Bungalow, Industrial Building, or Other?)
        - occupancy_status (Occupancy Status: Is it Self-occupied, Tenant-occupied, Vacant, or Unknown?)

        JSON Structure Example:
        {
            "owner_name": "",
            "father_husband_name": "",
            "survey_number": "",
            "plot_block_number": "",
            "village": "",
            "taluka": "",
            "district": "",
            "area_sq_meter": "",
            "area_sq_feet": "",
            "document_number": "",
            "registration_date": "",
            "sub_registrar_office": "",
            "boundary_east": "",
            "boundary_west": "",
            "boundary_north": "",
            "boundary_south": "",
            "property_type": "",
            "occupancy_status": "",
            "field_confidence": {
                "owner_name": "high",
                "father_husband_name": "high",
                "survey_number": "high",
                "plot_block_number": "high",
                "village": "high",
                "taluka": "high",
                "district": "high",
                "area_sq_meter": "high",
                "area_sq_feet": "high",
                "document_number": "high",
                "registration_date": "high",
                "sub_registrar_office": "high",
                "boundary_east": "high",
                "boundary_west": "high",
                "boundary_north": "high",
                "boundary_south": "high",
                "property_type": "high",
                "occupancy_status": "high"
            }
        }
        """,
        "7/12 Extract (Satbara)": """
        Analyze the provided images of a 7/12 Extract (Satbara Utara — VF-7 + VF-12, rural/agricultural land) document.
        Extract the following information and **TRANSLATE ALL VALUES TO ENGLISH**. The final output must be completely in professional English.
        If a field is not found, return an empty string or null.
        
        Also include a 'field_confidence' object mapping each field key to "high", "medium", or "low" based on how legible or certain the value was in the source image.
        
        Fields to extract:
        - village (Village)
        - taluka (Taluka)
        - district (District)
        - survey_number (Survey Number)
        - block_number (Block/Hissa Number)
        - khata_number (Khata Number)
        - owner_names (Owner(s)/Khatedar Name(s) & Share)
        - tenure_type (Tenure Type: Old/New Tenure)
        - total_area (Total Area)
        - land_type (Land Type: Agricultural/Non-Agri)
        - irrigation_source (Irrigation Source)
        - crop_details (Crop Details)
        - cultivator_name (Cultivator/Tenant Name)
        - mutation_entry_numbers (Mutation Entry No.s)
        - encumbrance_loan_details (Encumbrance/Loan Notation)
        - property_type (Property Type: Usually Agricultural Land)
        - occupancy_status (Occupancy Status)

        JSON Structure Example:
        {
            "village": "",
            "taluka": "",
            "district": "",
            "survey_number": "",
            "block_number": "",
            "khata_number": "",
            "owner_names": "",
            "tenure_type": "",
            "total_area": "",
            "land_type": "",
            "irrigation_source": "",
            "crop_details": "",
            "cultivator_name": "",
            "mutation_entry_numbers": "",
            "encumbrance_loan_details": "",
            "property_type": "",
            "occupancy_status": "",
            "field_confidence": {
                "village": "high",
                "taluka": "high",
                "district": "high",
                "survey_number": "high",
                "block_number": "high",
                "khata_number": "high",
                "owner_names": "high",
                "tenure_type": "high",
                "total_area": "high",
                "land_type": "high",
                "irrigation_source": "high",
                "crop_details": "high",
                "cultivator_name": "high",
                "mutation_entry_numbers": "high",
                "encumbrance_loan_details": "high",
                "property_type": "high",
                "occupancy_status": "high"
            }
        }
        """,
        "Property Card": """
        Analyze the provided images of a Property Card (urban/city survey land) document.
        Extract the following information and **TRANSLATE ALL VALUES TO ENGLISH**. The final output must be completely in professional English.
        If a field is not found, return an empty string or null.
        
        Also include a 'field_confidence' object mapping each field key to "high", "medium", or "low".
        
        Fields to extract:
        - city_survey_number (City Survey CTS Number: Look for સિટી સરવે નંબર)
        - city_survey_office (City Survey Office: Look for સિટી સરવે ઓફિસ)
        - ward (Ward: Look for વોર્ડ)
        - sheet_number (Sheet Number: Look for શીટ નંબર)
        - plot_number (Plot Number)
        - owner_names (Current Owner(s) & Share: Look for the most recent/last entry under 'નવો ધારણ કરનાર' or 'ધારણ કરનાર' in the mutation table)
        - area (Area: Look for ક્ષેત્રફળ)
        - tenure_type (Tenure Type)
        - land_use_type (Land Use: Residential/Commercial/Industrial)
        - mutation_entry_details (Mutation Entry Details)
        - encumbrance_details (Encumbrance Details)
        - property_tax_assessment_number (Property Tax Assessment No.)
        - boundary_east (East Boundary: Look for ચતુર્દિશા / East)
        - boundary_west (West Boundary: Look for ચતુર્દિશા / West)
        - boundary_north (North Boundary: Look for ચતુર્દિશા / North)
        - boundary_south (South Boundary: Look for ચતુર્દિશા / South)
        - property_type (Property Type: E.g., Land, Flat, Shop. Look at the latest mutation entry details to see if a 'ફ્લેટ' (Flat) or 'દુકાન' (Shop) is mentioned, otherwise default to Land.)
        - occupancy_status (Occupancy Status: Self-occupied, Tenant-occupied, Vacant)

        JSON Structure Example:
        {
            "city_survey_number": "",
            "city_survey_office": "",
            "ward": "",
            "sheet_number": "",
            "plot_number": "",
            "owner_names": "",
            "area": "",
            "tenure_type": "",
            "land_use_type": "",
            "mutation_entry_details": "",
            "encumbrance_details": "",
            "property_tax_assessment_number": "",
            "boundary_east": "",
            "boundary_west": "",
            "boundary_north": "",
            "boundary_south": "",
            "property_type": "",
            "occupancy_status": "",
            "field_confidence": {
                "city_survey_number": "high",
                "city_survey_office": "high",
                "ward": "high",
                "sheet_number": "high",
                "plot_number": "high",
                "owner_names": "high",
                "area": "high",
                "tenure_type": "high",
                "land_use_type": "high",
                "mutation_entry_details": "high",
                "encumbrance_details": "high",
                "property_tax_assessment_number": "high",
                "boundary_east": "high",
                "boundary_west": "high",
                "boundary_north": "high",
                "boundary_south": "high",
                "property_type": "high",
                "occupancy_status": "high"
            }
        }
        """,
        "Index-II": """
        Analyze the provided images of an Index-II (registration summary) document.
        Extract the following information and **TRANSLATE ALL VALUES TO ENGLISH**. The final output must be completely in professional English.
        If a field is not found, return an empty string or null.
        
        Also include a 'field_confidence' object.
        
        Fields to extract:
        - document_number (Document Number)
        - registration_date (Registration Date)
        - sub_registrar_office (Sub-Registrar Office)
        - document_type (Document Type: Sale/Mortgage/Gift)
        - executant_name (Executant/Seller Name: વેચનારનું નામ)
        - claimant_name (Claimant/Buyer Name: ખરીદનારનું નામ)
        - property_description (Property Description: survey no., village, area)
        - agreement_value (Agreement/Consideration Value)
        - jantri_value (Jantri Value)
        - stamp_duty_paid (Stamp Duty Paid)
        - registration_fee_paid (Registration Fee Paid)
        - property_type (Property Type: Land, Flat, Shop, Rowhouse, Bungalow, Industrial Building)
        - occupancy_status (Occupancy Status: Self-occupied, Tenant-occupied, Vacant)

        JSON Structure Example:
        {
            "document_number": "",
            "registration_date": "",
            "sub_registrar_office": "",
            "document_type": "",
            "executant_name": "",
            "claimant_name": "",
            "property_description": "",
            "agreement_value": "",
            "jantri_value": "",
            "stamp_duty_paid": "",
            "registration_fee_paid": "",
            "property_type": "",
            "occupancy_status": "",
            "field_confidence": {
                "document_number": "high",
                "registration_date": "high",
                "sub_registrar_office": "high",
                "document_type": "high",
                "executant_name": "high",
                "claimant_name": "high",
                "property_description": "high",
                "agreement_value": "high",
                "jantri_value": "high",
                "stamp_duty_paid": "high",
                "registration_fee_paid": "high",
                "property_type": "high",
                "occupancy_status": "high"
            }
        }
        """
    }

    # Append critical JSON formatting instruction to all prompts
    for key in PROMPTS:
        PROMPTS[key] += "\n\nCRITICAL: Ensure the output is STRICTLY valid JSON. You must escape any double quotes (\\\") and newlines (\\\\n) inside string values. Do not truncate the JSON output."

    prompt = PROMPTS.get(document_type, PROMPTS["Dastavej (Sale Deed)"])

    # puting the prompt and images together to send to gemini
    content_parts = [prompt] + images

    response = None
    model_errors = []
    # try different models until one works
    for model_name in _get_supported_model_candidates(api_key):
        try:
            model = genai.GenerativeModel(
                model_name=model_name,
                generation_config=generation_config,
            )
            # send everything to the ai and get the response
            response = model.generate_content(content_parts)
            break
        except Exception as e:
            model_errors.append(f"{model_name}: {str(e)}")

    if response is None:
        return {
            "error": "Could not access any supported Gemini Flash model. Please check your API key or internet.",
            "details": model_errors,
        }

    # now parse the response into actual data
    try:
        raw_response = (response.text or "").strip()
        
        # clean up if ai added markdown code blocks
        if raw_response.startswith("```"):
            raw_response = re.sub(r'^```(?:json)?\s*', '', raw_response)
            raw_response = re.sub(r'\s*```$', '', raw_response)
            
        # Fix common LLM JSON errors like trailing commas before brackets/braces
        raw_response = re.sub(r',\s*([\]}])', r'\1', raw_response)

        try:
            data = json.loads(raw_response, strict=False)
        except json.JSONDecodeError:
            # Invincible fallback: scans for keys and grabs everything in between
            data = {}
            # match keys in quotes followed by a colon
            matches = list(re.finditer(r'"([a-zA-Z_0-9]+)"\s*:', raw_response))
            for i in range(len(matches)):
                k = matches[i].group(1)
                start = matches[i].end()
                # Value goes until the next key starts, or end of string
                end = matches[i+1].start() if i + 1 < len(matches) else len(raw_response)
                
                val_str = raw_response[start:end].strip()
                # Clean up trailing commas, brackets, or spaces
                val_str = re.sub(r'[,}\s]+$', '', val_str)
                # Remove surrounding quotes if they exist
                if val_str.startswith('"'): val_str = val_str[1:]
                if val_str.endswith('"'): val_str = val_str[:-1]
                
                # Ignore nested objects like field_confidence
                if not val_str.startswith('{'):
                    data[k] = val_str
            
            if not data:
                raise Exception(f"AI response was completely unreadable. Raw response: {raw_response}")

        return data
    except Exception as e:
        return {"error": f"Failed to read AI response: {str(e)}", "raw_response": getattr(response, 'text', '')}
