import fitz  
import google.generativeai as genai  
import json    
import io     
import re     
from PIL import Image 

def get_pdf_images(pdf_content):
    # ok so basically we need to turn each pdf page into an image
    # because the ai needs to see it as a picture to understand whats going on
   
    doc = fitz.open(stream=pdf_content, filetype="pdf")
    images = []
    for page_num in range(len(doc)):
        # grab this specific page
        page = doc.load_page(page_num)
        # turn it in a pixmap thing, making it twice as big so its clearer
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  
        # convert it to png bytes
        img_data = pix.tobytes("png")
        # throw it in our images list
        images.append(Image.open(io.BytesIO(img_data)))
    return images


def _get_supported_model_candidates():
   
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

def extract_structured_data(api_key, pdf_content):
    # main function 
    genai.configure(api_key=api_key)
    
    #  settings to tell the ai how to behave
    generation_config = {
        "temperature": 0.1,  # low temperature means more precise, less random
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_mime_type": "application/json",  # make sure ai gives us json back
    }

    # first turning the pdf pages into images
    images = get_pdf_images(pdf_content)
    
    # this is prompt with all the instructions for the ai
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

    # puting the prompt and images together to send to gemini
    content_parts = [prompt] + images

    response = None
    model_errors = []
    # try different models until one works
    for model_name in _get_supported_model_candidates():
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
            raw_response = raw_response.strip("`")
            raw_response = raw_response.replace("json", "", 1).strip()

        try:
            data = json.loads(raw_response)
        except json.JSONDecodeError:
            # if theres extra text around the json, try to find just the json part
            match = re.search(r"\{.*\}", raw_response, re.DOTALL)
            if not match:
                raise
            data = json.loads(match.group(0))

        return data
    except Exception as e:
        return {"error": f"Failed to read AI response: {str(e)}", "raw_response": response.text}
