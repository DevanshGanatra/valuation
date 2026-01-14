import fitz  # PyMuPDF
import google.generativeai as genai
import json
import io
from PIL import Image

def get_pdf_images(pdf_content):
    """Converts PDF pages into images."""
    doc = fitz.open(stream=pdf_content, filetype="pdf")
    images = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # Better quality
        img_data = pix.tobytes("png")
        images.append(Image.open(io.BytesIO(img_data)))
    return images

def extract_structured_data(api_key, pdf_content):
    """
    Uses Gemini 1.5 Flash to extract structured data from PDF images.
    Gemini supports both text and image input simultaneously.
    """
    genai.configure(api_key=api_key)
    
    # Configuration for the model
    generation_config = {
        "temperature": 0.1,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_mime_type": "application/json",
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
    )

    images = get_pdf_images(pdf_content)
    
    # Prepare the prompt
    prompt = """
    Analyze the provided images of a Gujarati property document (Dastavej). 
    Extract the following information in Gujarati (where applicable) and return it in a strictly structured JSON format.
    If a field is not found, return an empty string or null.
    
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
        "boundary_south": ""
    }
    """

    # We send images to Gemini. Note: Gemini 1.5 Flash has a large context window.
    # For very large PDFs, we might need to be selective, but usually Dastavejs are a few pages.
    content_parts = [prompt] + images

    response = model.generate_content(content_parts)
    
    try:
        data = json.loads(response.text)
        return data
    except Exception as e:
        return {"error": f"Failed to parse AI response: {str(e)}", "raw_response": response.text}
