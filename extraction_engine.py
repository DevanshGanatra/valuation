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
   
    preferred = ["gemini-2.0-flash", "gemini-1.5-flash-latest"]
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
        Analyze the provided images of a Gujarati property document (Dastavej). 
        Extract the following information in Gujarati (where applicable) and return it in a strictly structured JSON format.
        If a field is not found, return an empty string or null.
        
        Also include a 'field_confidence' object mapping each field key to "high", "medium", or "low" based on how legible or certain the value was in the source image.
        
        Fields to extract:
        - owner_name (Owner Name / માલિકનું નામ)
        - father_husband_name (Father / Husband Name / પિતા અથવા પતિનું નામ)
        - survey_number (Survey Number / સર્વે નંબર)
        - plot_block_number (Plot / Block Number / પ્લોટ અથવા બ્લોક નંબર)
        - village (Village / ગામ)
        - taluka (Taluka / તાલુકો)
        - district (District / જિલ્લો)
        - area_sq_meter (Area in Sq. Meter / ક્ષેત્રફળ ચો.મી. માં)
        - area_sq_feet (Area in Sq. Feet / ક્ષેત્રફળ ચો.ફુટ માં)
        - document_number (Document Number / દસ્તાવેજ નંબર)
        - registration_date (Registration Date / રજીસ્ટ્રેશન તારીખ - DD/MM/YYYY)
        - sub_registrar_office (Sub-Registrar Office / સબ-રજીસ્ટ્રાર કચેરી)
        - boundary_east (East Boundary / પૂર્વ દિશાની વિગત)
        - boundary_west (West Boundary / પશ્ચિમ દિશાની વિગત)
        - boundary_north (North Boundary / ઉત્તર દિશાની વિગત)
        - boundary_south (South Boundary / દક્ષિણ દિશાની વિગત)

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
                "boundary_south": "high"
            }
        }
        """,
        "7/12 Extract (Satbara)": """
        Analyze the provided images of a 7/12 Extract (Satbara Utara — VF-7 + VF-12, rural/agricultural land) document.
        Extract the following information in Gujarati (where applicable) and return it in a strictly structured JSON format.
        If a field is not found, return an empty string or null.
        
        Also include a 'field_confidence' object mapping each field key to "high", "medium", or "low" based on how legible or certain the value was in the source image.
        
        Fields to extract:
        - village (Village / ગામ)
        - taluka (Taluka / તાલુકો)
        - district (District / જિલ્લો)
        - survey_number (Survey Number / સર્વે નંબર)
        - block_number (Block/Hissa Number / બ્લોક નંબર)
        - khata_number (Khata Number / ખાતા નંબર)
        - owner_names (Owner(s)/Khatedar Name(s) & Share / ખાતેદારનું નામ)
        - tenure_type (Tenure Type (Old/New Tenure) / સત્તા પ્રકાર (જૂની/નવી શરત))
        - total_area (Total Area / કુલ ક્ષેત્રફળ)
        - land_type (Land Type (Agricultural/Non-Agri) / જમીનનો પ્રકાર)
        - irrigation_source (Irrigation Source / પિયતનો સ્ત્રોત)
        - crop_details (Crop Details (VF-12) / પાક વિગત)
        - cultivator_name (Cultivator/Tenant Name (if different from owner) / ખેડૂત/ગણોતિયાનું નામ)
        - mutation_entry_numbers (Mutation Entry No.s (VF-6 references) / હક્ક નોંધ નંબર)
        - encumbrance_loan_details (Encumbrance/Loan Notation / બોજા/લોનની વિગત)

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
                "encumbrance_loan_details": "high"
            }
        }
        """,
        "Property Card": """
        Analyze the provided images of a Property Card (urban/city survey land, issued by City Survey Office) document.
        Extract the following information in Gujarati (where applicable) and return it in a strictly structured JSON format.
        If a field is not found, return an empty string or null.
        
        Also include a 'field_confidence' object mapping each field key to "high", "medium", or "low" based on how legible or certain the value was in the source image.
        
        Fields to extract:
        - city_survey_number (City Survey (CTS) Number / સીટી સર્વે નંબર)
        - city_survey_office (City Survey Office / સીટી સર્વે ઓફિસ)
        - ward (Ward / વોર્ડ)
        - sheet_number (Sheet Number / શીટ નંબર)
        - plot_number (Plot Number / પ્લોટ નંબર)
        - owner_names (Owner(s) & Share / માલિકનું નામ અને હિસ્સો)
        - area (Area / ક્ષેત્રફળ)
        - tenure_type (Tenure Type / સત્તા પ્રકાર)
        - land_use_type (Land Use (Residential/Commercial/Industrial) / વપરાશનો પ્રકાર)
        - mutation_entry_details (Mutation Entry Details / દાખલ નોંધ વિગત)
        - encumbrance_details (Encumbrance Details / બોજા/હક્કપત્રકની વિગત)
        - property_tax_assessment_number (Property Tax Assessment No. / મિલકત વેરા મૂલ્યાંકન નંબર)
        - boundary_east (East Boundary / પૂર્વ દિશાની વિગત)
        - boundary_west (West Boundary / પશ્ચિમ દિશાની વિગત)
        - boundary_north (North Boundary / ઉત્તર દિશાની વિગત)
        - boundary_south (South Boundary / દક્ષિણ દિશાની વિગત)

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
                "boundary_south": "high"
            }
        }
        """,
        "Index-II": """
        Analyze the provided images of an Index-II (Garvi/Sub-Registrar one-page registration summary) document.
        Extract the following information in Gujarati (where applicable) and return it in a strictly structured JSON format.
        If a field is not found, return an empty string or null.
        
        Also include a 'field_confidence' object mapping each field key to "high", "medium", or "low" based on how legible or certain the value was in the source image.
        
        Fields to extract:
        - document_number (Document Number / દસ્તાવેજ નંબર)
        - registration_date (Registration Date / નોંધણી તારીખ)
        - sub_registrar_office (Sub-Registrar Office / સબ રજિસ્ટ્રાર કચેરી)
        - document_type (Document Type (Sale/Mortgage/Gift, etc.) / દસ્તાવેજનો પ્રકાર)
        - executant_name (Executant/Seller Name / કરનાર/વેચનારનું નામ)
        - claimant_name (Claimant/Buyer Name / લેનાર/ખરીદનારનું નામ)
        - property_description (Property Description (survey no., village, area) / મિલકતનું વર્ણન)
        - agreement_value (Agreement/Consideration Value / દસ્તાવેજની કિંમત)
        - jantri_value (Jantri (Govt. Guideline) Value / જંત્રી કિંમત)
        - stamp_duty_paid (Stamp Duty Paid / સ્ટેમ્પ ડ્યુટી)
        - registration_fee_paid (Registration Fee Paid / નોંધણી ફી)

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
                "registration_fee_paid": "high"
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
            # if theres extra text around the json, try to find just the json part
            match = re.search(r"\{.*\}", raw_response, re.DOTALL)
            if not match:
                raise
            json_str = match.group(0)
            # fix trailing commas again just in case
            json_str = re.sub(r',\s*([\]}])', r'\1', json_str)
            try:
                data = json.loads(json_str, strict=False)
            except json.JSONDecodeError:
                # Absolute fallback for hopelessly broken or truncated JSON
                data = {}
                pairs = re.findall(r'"([a-zA-Z_0-9]+)"\s*:\s*"(.*?)"(?=\s*[,}\n]|$)', json_str)
                for k, v in pairs:
                    data[k] = v
                if not data:
                    raise

        return data
    except Exception as e:
        return {"error": f"Failed to read AI response: {str(e)}", "raw_response": response.text}
