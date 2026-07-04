import streamlit as st  
import base64         
from extraction_engine import extract_structured_data  
from utils import convert_sqm_to_sqft, generate_excel, generate_pdf_report, extract_numeric_value, parse_hectare_are_sqm  
import hashlib       

st.set_page_config(page_title=" Dastavej AI Valuator", layout="wide")

st.markdown("""
    <style>
    /* Import Premium Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    /* Base Typography */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        color: #1e293b !important;
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.03em !important;
        background: linear-gradient(135deg, #0f172a 0%, #334155 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem !important;
    }

    /* Dynamic Animated Background */
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    .stApp {
        background: linear-gradient(-45deg, #f8fafc, #e0e7ff, #f0fdf4, #f8fafc);
        background-size: 400% 400%;
        animation: gradientBG 20s ease infinite;
    }

    /* Entrance Animations */
    @keyframes slideUpFade {
        0% { opacity: 0; transform: translateY(30px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    .block-container {
        animation: slideUpFade 1s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }

    /* Stunning Glassmorphism Forms */
    .stForm {
        background: rgba(255, 255, 255, 0.45) !important;
        backdrop-filter: blur(20px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
        border: 1px solid rgba(255, 255, 255, 0.6) !important;
        border-radius: 24px !important;
        padding: 35px !important;
        box-shadow: 
            0 20px 40px rgba(0, 0, 0, 0.04), 
            inset 0 1px 0 rgba(255, 255, 255, 0.9),
            inset 0 0 20px rgba(255, 255, 255, 0.5) !important;
        transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.4s ease;
    }
    .stForm:hover {
        transform: translateY(-4px);
        box-shadow: 0 30px 60px rgba(0, 0, 0, 0.06), inset 0 1px 0 rgba(255, 255, 255, 0.9) !important;
    }

    /* Input Fields - Neumorphic / Glass blend */
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        background-color: rgba(255, 255, 255, 0.7) !important;
        border: 1px solid rgba(226, 232, 240, 0.8) !important;
        border-radius: 12px !important;
        color: #0f172a !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 500 !important;
        font-size: 1.05rem !important;
        padding: 14px 18px !important;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.02) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus {
        background-color: #ffffff !important;
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.15), inset 0 1px 2px rgba(0,0,0,0.01) !important;
        transform: translateY(-1px);
    }

    /* Input Labels */
    .stTextInput label, .stTextArea label, .stFileUploader label {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        color: #475569 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 8px;
    }

    /* File Uploader - Dashed Animated Area */
    [data-testid="stFileUploader"] {
        background: rgba(255, 255, 255, 0.5);
        border: 2px dashed #cbd5e1;
        border-radius: 20px;
        padding: 30px;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }
    [data-testid="stFileUploader"]:hover {
        border-color: #3b82f6;
        background: rgba(255, 255, 255, 0.8);
        box-shadow: 0 10px 25px rgba(59, 130, 246, 0.1);
        transform: scale(1.01);
    }

    /* Hero Button Style */
    .stButton>button, .stFormSubmitButton>button, .stDownloadButton>button {
        width: 100%;
        border-radius: 14px;
        height: 3.5rem;
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: #ffffff !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 700 !important;
        font-size: 1.15rem !important;
        letter-spacing: 0.02em;
        border: none;
        box-shadow: 0 10px 20px -5px rgba(29, 78, 216, 0.4);
        position: relative;
        overflow: hidden;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        z-index: 1;
    }

    /* Button Shine Effect */
    .stButton>button::before, .stFormSubmitButton>button::before, .stDownloadButton>button::before {
        content: '';
        position: absolute;
        top: 0; left: -100%; width: 50%; height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.25), transparent);
        transform: skewX(-20deg);
        transition: all 0.5s ease;
        z-index: -1;
    }
    .stButton>button:hover::before, .stFormSubmitButton>button:hover::before, .stDownloadButton>button:hover::before {
        left: 150%;
    }

    .stButton>button:hover, .stFormSubmitButton>button:hover, .stDownloadButton>button:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 15px 25px -5px rgba(29, 78, 216, 0.5);
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        border: none;
    }
    
    .stButton>button:active, .stFormSubmitButton>button:active, .stDownloadButton>button:active {
        transform: translateY(0) scale(1);
    }

    /* Sidebar Ultra Premium styling */
    [data-testid="stSidebar"] {
        background: rgba(248, 250, 252, 0.7) !important;
        backdrop-filter: blur(30px) !important;
        -webkit-backdrop-filter: blur(30px) !important;
        border-right: 1px solid rgba(255,255,255,0.6);
        box-shadow: 5px 0 40px rgba(0,0,0,0.03);
    }

    /* Alerts and Info Boxes */
    .stAlert {
        border-radius: 16px !important;
        border: 1px solid rgba(255,255,255,0.8) !important;
        background: rgba(255, 255, 255, 0.6) !important;
        backdrop-filter: blur(10px) !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03) !important;
    }

    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    ::-webkit-scrollbar-track {
        background: rgba(0,0,0,0.02); 
    }
    ::-webkit-scrollbar-thumb {
        background: #cbd5e1; 
        border-radius: 10px;
        border: 2px solid transparent;
        background-clip: padding-box;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #94a3b8; 
        border: 2px solid transparent;
        background-clip: padding-box;
    }

    /* Top bar color hiding */
    header[data-testid="stHeader"] {
        background: transparent !important;
    }

    /* Image container styling */
    div[data-testid="stImage"] img {
        border-radius: 16px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08);
        border: 1px solid rgba(0,0,0,0.05);
    }
    
    /* Skeleton Loading Animation */
    .skeleton-container {
        background: rgba(255, 255, 255, 0.45);
        backdrop-filter: blur(20px) saturate(180%);
        -webkit-backdrop-filter: blur(20px) saturate(180%);
        border: 1px solid rgba(255, 255, 255, 0.6);
        border-radius: 24px;
        padding: 35px;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.04);
        margin-bottom: 20px;
    }
    .skeleton-title {
        height: 28px;
        width: 35%;
        margin-bottom: 25px;
        border-radius: 8px;
        background: linear-gradient(90deg, rgba(226, 232, 240, 0.6) 25%, rgba(241, 245, 249, 0.8) 50%, rgba(226, 232, 240, 0.6) 75%);
        background-size: 200% 100%;
        animation: skeleton-shimmer 2s infinite linear;
    }
    .skeleton-input {
        height: 48px;
        margin-bottom: 20px;
        border-radius: 12px;
        background: linear-gradient(90deg, rgba(226, 232, 240, 0.6) 25%, rgba(241, 245, 249, 0.8) 50%, rgba(226, 232, 240, 0.6) 75%);
        background-size: 200% 100%;
        animation: skeleton-shimmer 2s infinite linear;
    }
    .skeleton-row {
        display: flex;
        gap: 15px;
        width: 100%;
    }
    @keyframes skeleton-shimmer {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; margin-top: 1rem; margin-bottom: 3.5rem; animation: slideUpFade 0.8s ease-out;">
    <h1 style="font-size: 4.2rem; font-family: 'Outfit', sans-serif; font-weight: 800; background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #06b6d4 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.8rem; letter-spacing: -0.04em; padding-top: 20px;">
        AI Valuator
    </h1>
    <h3 style="font-size: 1.5rem; color: #475569; font-weight: 500; font-family: 'Plus Jakarta Sans', sans-serif; margin-bottom: 1rem;">
        Gujarati Dastavej Intelligence
    </h3>
    <p style="font-size: 1.15rem; color: #64748b; font-family: 'Plus Jakarta Sans', sans-serif; max-width: 650px; margin: 0 auto; line-height: 1.7; font-weight: 400;">
        Transform complex legal property documents into structured valuation data <b>instantly</b> using advanced Vision-Language Architecture.
    </p>
</div>
""", unsafe_allow_html=True)


with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    st.info("💡 Your API key is used only for processing and is not stored.")
    st.markdown("---")
    
    st.markdown("### Instructions")
    st.write("1. Upload a Gujarati Dastavej PDF.")
    st.write("2. AI will extract data automatically.")
    st.write("3. Review and edit the pre-filled form.")
    st.write("4. Download the final report.")
    
    st.markdown("---")
    st.markdown("### ✨ Project Credits")
    st.success("Project by **Devansh Ganatra**")

# main logic
if not api_key:
    # warning
    st.warning("Please enter your Gemini API Key in the sidebar to begin.")
else:
    document_type = st.selectbox(
        "Select Document Type",
        options=["Dastavej (Sale Deed)", "7/12 Extract (Satbara)", "Property Card", "Index-II"]
    )
    
    if st.session_state.get("last_document_type") != document_type:
        st.session_state.pop("extracted_data", None)
        st.session_state.pop("final_data", None)
        st.session_state.pop("pdf_preview_images", None)
        st.session_state.last_document_type = document_type

    uploaded_file = st.file_uploader(f"Upload {document_type} (PDF)", type=["pdf"])

    if uploaded_file is not None:
        # get the pdf bytes
        uploaded_pdf_bytes = uploaded_file.getvalue()
        
        # make a unique id for this file based on its content
        file_hash = hashlib.sha256(uploaded_pdf_bytes).hexdigest()
        
        # if its a different file, clear the old stuff
        if st.session_state.get("last_uploaded_file_hash") != file_hash:
            st.session_state.pop("extracted_data", None)
            st.session_state.pop("final_data", None)
            st.session_state.pop("pdf_preview_images", None)
            st.session_state.last_uploaded_file_hash = file_hash

        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("PDF Preview")
            
            # Using get_pdf_images to render PDF reliably instead of buggy base64 embeds
            with st.spinner("Loading document preview..."):
                if "pdf_preview_images" not in st.session_state:
                    try:
                        import fitz
                        doc = fitz.open(stream=uploaded_pdf_bytes, filetype="pdf")
                        images = []
                        # Max 10 pages for preview to keep the UI snappy and avoid double high-res processing
                        for page_num in range(min(len(doc), 10)):
                            page = doc.load_page(page_num)
                            pix = page.get_pixmap(matrix=fitz.Matrix(1, 1))
                            images.append(pix.tobytes("jpeg"))
                        st.session_state.pdf_preview_images = images
                    except Exception as e:
                        st.error(f"Error reading PDF: {e}")
                
                if "pdf_preview_images" in st.session_state:
                    with st.container(height=800, border=True):
                        for img in st.session_state.pdf_preview_images:
                            st.image(img, use_container_width=True)

        with col2:
            st.subheader("Extracted Details & Form")
            
            # first time? run the ai to extract data
            if 'extracted_data' not in st.session_state:
                import fitz
                doc_check = fitz.open(stream=uploaded_pdf_bytes, filetype="pdf")
                num_pages = len(doc_check)
                doc_check.close()

                if num_pages > 15:
                    st.warning(f"This document has {num_pages} pages. Processing long documents may take longer and cost more in API usage.")
                    proceed = st.checkbox("I understand, process anyway")
                    if not proceed:
                        st.stop()

                # Skeleton HTML representation to show while loading
                skeleton_html = """
                <div class="skeleton-container">
                    <div class="skeleton-title"></div>
                    <div class="skeleton-input" style="width: 100%;"></div>
                    <div class="skeleton-input" style="width: 100%;"></div>
                    <div class="skeleton-title" style="margin-top: 30px; width: 45%;"></div>
                    <div class="skeleton-row">
                        <div class="skeleton-input" style="width: 33%;"></div>
                        <div class="skeleton-input" style="width: 33%;"></div>
                        <div class="skeleton-input" style="width: 33%;"></div>
                    </div>
                    <div class="skeleton-title" style="margin-top: 30px; width: 50%;"></div>
                    <div class="skeleton-row">
                        <div class="skeleton-input" style="width: 50%;"></div>
                        <div class="skeleton-input" style="width: 50%;"></div>
                    </div>
                </div>
                """
                skeleton_placeholder = st.empty()
                skeleton_placeholder.markdown(skeleton_html, unsafe_allow_html=True)

                with st.spinner("AI is converting legal text to structured data..."):
                    try:
                        # call to the extraction engine to get the data
                        extracted_data = extract_structured_data(api_key, uploaded_pdf_bytes, document_type)
                        # clear skeleton when done
                        skeleton_placeholder.empty()
                        
                        if "error" in extracted_data:
                            st.error(extracted_data["error"])
                            st.stop()

                        st.session_state.extracted_data = extracted_data
                        st.toast("Extraction complete!", icon="✅")
                    except Exception as e:
                        skeleton_placeholder.empty()
                        st.error(f"An error occurred: {str(e)}")
                        st.stop()
            
            data = st.session_state.extracted_data

            # Robustness fix: Sometimes LLMs return a JSON Array instead of an Object
            if isinstance(data, list) and len(data) > 0:
                data = data[0]
                
            # If for any reason data is still not a dictionary, fall back to empty dict
            if not isinstance(data, dict):
                data = {}

        
            st.markdown("### Valuation Calculation")
            vc1, vc2 = st.columns(2)
            rate_per_sqft = vc1.number_input("Rate per Sq. Ft. (₹)", value=0.0, step=100.0)
            property_age_years = vc2.number_input("Property Age (years)", value=0, step=1)
            
            calc_area_sqm = data.get("area_sq_meter", "")
            calc_area_sqft = data.get("area_sq_feet", "")
            
            # fallback to generic area fields for other document types if missing
            if not calc_area_sqft and not calc_area_sqm:
                calc_area_sqm = data.get("area", "") or data.get("total_area", "")

            if document_type == "7/12 Extract (Satbara)":
                hectare_sqm = parse_hectare_are_sqm(calc_area_sqm)
                if hectare_sqm is not None:
                    calc_area_sqm = hectare_sqm

            if calc_area_sqm and not calc_area_sqft:
                calc_area_sqft = convert_sqm_to_sqft(calc_area_sqm)
            
            try:
                area_val = extract_numeric_value(calc_area_sqft)
            except:
                area_val = 0.0

            depreciation_pct = min(property_age_years * 1, 30) / 100.0
            base_value = area_val * rate_per_sqft
            estimated_value = base_value * (1.0 - depreciation_pct)

            st.metric("Estimated Property Value", f"₹ {estimated_value:,.2f}")
            st.markdown("---")

            with st.form("valuation_form"):
                form_data = {"document_type": document_type}
                
                def render_confidence(key, container=st):
                    conf = data.get("field_confidence", {}).get(key)
                    if conf == "low":
                        container.caption("⚠ Please verify — AI was not fully confident")
                    elif conf == "medium":
                        container.caption("Please double-check")
                
                if document_type == "7/12 Extract (Satbara)":
                    st.markdown("### Location Details")
                    c1, c2, c3 = st.columns(3)
                    form_data["village"] = c1.text_input("Village (ગામ)", value=data.get("village", ""))
                    render_confidence("village", c1)
                    form_data["taluka"] = c2.text_input("Taluka (તાલુકો)", value=data.get("taluka", ""))
                    render_confidence("taluka", c2)
                    form_data["district"] = c3.text_input("District (જિલ્લો)", value=data.get("district", ""))
                    render_confidence("district", c3)
                    
                    st.markdown("### Property Identification")
                    st.link_button("Verify on AnyROR ↗", "https://anyror.gujarat.gov.in/")
                    c4, c5, c6 = st.columns(3)
                    form_data["survey_number"] = c4.text_input("Survey Number", value=data.get("survey_number", ""))
                    render_confidence("survey_number", c4)
                    form_data["block_number"] = c5.text_input("Block/Hissa Number", value=data.get("block_number", ""))
                    render_confidence("block_number", c5)
                    form_data["khata_number"] = c6.text_input("Khata Number", value=data.get("khata_number", ""))
                    render_confidence("khata_number", c6)

                    st.markdown("### Ownership & Tenure")
                    form_data["owner_names"] = st.text_area("Owner(s)/Khatedar Name(s) & Share", value=data.get("owner_names", ""))
                    render_confidence("owner_names")
                    form_data["tenure_type"] = st.text_input("Tenure Type (Old/New)", value=data.get("tenure_type", ""))
                    render_confidence("tenure_type")

                    st.markdown("### Area & Cultivation")
                    c7, c8 = st.columns(2)
                    form_data["total_area"] = c7.text_input("Total Area", value=data.get("total_area", ""))
                    render_confidence("total_area", c7)
                    form_data["land_type"] = c8.text_input("Land Type", value=data.get("land_type", ""))
                    render_confidence("land_type", c8)
                    c9, c10 = st.columns(2)
                    form_data["irrigation_source"] = c9.text_input("Irrigation Source", value=data.get("irrigation_source", ""))
                    render_confidence("irrigation_source", c9)
                    form_data["cultivator_name"] = c10.text_input("Cultivator/Tenant Name", value=data.get("cultivator_name", ""))
                    render_confidence("cultivator_name", c10)
                    form_data["crop_details"] = st.text_area("Crop Details", value=data.get("crop_details", ""))
                    render_confidence("crop_details")

                    st.markdown("### Mutation & Encumbrance")
                    form_data["mutation_entry_numbers"] = st.text_area("Mutation Entry No.s", value=data.get("mutation_entry_numbers", ""))
                    render_confidence("mutation_entry_numbers")
                    form_data["encumbrance_loan_details"] = st.text_area("Encumbrance/Loan Notation", value=data.get("encumbrance_loan_details", ""))
                    render_confidence("encumbrance_loan_details")
                    
                    form_area_val = form_data["total_area"]

                elif document_type == "Property Card":
                    st.markdown("### City Survey Details")
                    st.link_button("Verify on AnyROR ↗", "https://anyror.gujarat.gov.in/")
                    c1, c2 = st.columns(2)
                    form_data["city_survey_number"] = c1.text_input("City Survey (CTS) Number", value=data.get("city_survey_number", ""))
                    render_confidence("city_survey_number", c1)
                    form_data["city_survey_office"] = c2.text_input("City Survey Office", value=data.get("city_survey_office", ""))
                    render_confidence("city_survey_office", c2)
                    
                    c3, c4, c5 = st.columns(3)
                    form_data["ward"] = c3.text_input("Ward", value=data.get("ward", ""))
                    render_confidence("ward", c3)
                    form_data["sheet_number"] = c4.text_input("Sheet Number", value=data.get("sheet_number", ""))
                    render_confidence("sheet_number", c4)
                    form_data["plot_number"] = c5.text_input("Plot Number", value=data.get("plot_number", ""))
                    render_confidence("plot_number", c5)

                    st.markdown("### Ownership & Tenure")
                    form_data["owner_names"] = st.text_area("Owner(s) & Share", value=data.get("owner_names", ""))
                    render_confidence("owner_names")
                    c6, c7 = st.columns(2)
                    form_data["tenure_type"] = c6.text_input("Tenure Type", value=data.get("tenure_type", ""))
                    render_confidence("tenure_type", c6)
                    form_data["land_use_type"] = c7.text_input("Land Use", value=data.get("land_use_type", ""))
                    render_confidence("land_use_type", c7)

                    st.markdown("### Area & Taxes")
                    c8, c9 = st.columns(2)
                    form_data["area"] = c8.text_input("Area", value=data.get("area", ""))
                    render_confidence("area", c8)
                    form_data["property_tax_assessment_number"] = c9.text_input("Tax Assessment No.", value=data.get("property_tax_assessment_number", ""))
                    render_confidence("property_tax_assessment_number", c9)

                    st.markdown("### Boundary Details")
                    b1, b2 = st.columns(2)
                    form_data["boundary_east"] = b1.text_area("East (પૂર્વ)", value=data.get("boundary_east", ""))
                    render_confidence("boundary_east", b1)
                    form_data["boundary_west"] = b2.text_area("West (પશ્ચિમ)", value=data.get("boundary_west", ""))
                    render_confidence("boundary_west", b2)
                    b3, b4 = st.columns(2)
                    form_data["boundary_north"] = b3.text_area("North (ઉત્તર)", value=data.get("boundary_north", ""))
                    render_confidence("boundary_north", b3)
                    form_data["boundary_south"] = b4.text_area("South (દક્ષિણ)", value=data.get("boundary_south", ""))
                    render_confidence("boundary_south", b4)

                    st.markdown("### Mutation & Encumbrance")
                    form_data["mutation_entry_details"] = st.text_area("Mutation Entry Details", value=data.get("mutation_entry_details", ""))
                    render_confidence("mutation_entry_details")
                    form_data["encumbrance_details"] = st.text_area("Encumbrance Details", value=data.get("encumbrance_details", ""))
                    render_confidence("encumbrance_details")

                    form_area_val = form_data["area"]

                elif document_type == "Index-II":
                    st.markdown("### Registration Details")
                    c1, c2 = st.columns(2)
                    form_data["document_number"] = c1.text_input("Document Number", value=data.get("document_number", ""))
                    render_confidence("document_number", c1)
                    form_data["document_type"] = c2.text_input("Document Type", value=data.get("document_type", ""))
                    render_confidence("document_type", c2)
                    c3, c4 = st.columns(2)
                    form_data["registration_date"] = c3.text_input("Registration Date", value=data.get("registration_date", ""))
                    render_confidence("registration_date", c3)
                    form_data["sub_registrar_office"] = c4.text_input("Sub-Registrar Office", value=data.get("sub_registrar_office", ""))
                    render_confidence("sub_registrar_office", c4)

                    st.markdown("### Parties")
                    form_data["executant_name"] = st.text_area("Executant/Seller Name", value=data.get("executant_name", ""))
                    render_confidence("executant_name")
                    form_data["claimant_name"] = st.text_area("Claimant/Buyer Name", value=data.get("claimant_name", ""))
                    render_confidence("claimant_name")

                    st.markdown("### Property Details")
                    form_data["property_description"] = st.text_area("Property Description", value=data.get("property_description", ""))
                    render_confidence("property_description")

                    st.markdown("### Financial Details")
                    f1, f2 = st.columns(2)
                    form_data["agreement_value"] = f1.text_input("Agreement/Consideration Value", value=data.get("agreement_value", ""))
                    render_confidence("agreement_value", f1)
                    form_data["jantri_value"] = f2.text_input("Jantri Value", value=data.get("jantri_value", ""))
                    render_confidence("jantri_value", f2)
                    f3, f4 = st.columns(2)
                    form_data["stamp_duty_paid"] = f3.text_input("Stamp Duty Paid", value=data.get("stamp_duty_paid", ""))
                    render_confidence("stamp_duty_paid", f3)
                    form_data["registration_fee_paid"] = f4.text_input("Registration Fee Paid", value=data.get("registration_fee_paid", ""))
                    render_confidence("registration_fee_paid", f4)
                    
                    form_area_val = "0.0"

                else:
                    st.markdown("### Owner Details")
                    form_data["owner_name"] = st.text_input("Owner Name (માલિકનું નામ)", value=data.get("owner_name", ""))
                    render_confidence("owner_name")
                    form_data["father_husband_name"] = st.text_input("Father / Husband Name (પિતા અથવા પતિનું નામ)", value=data.get("father_husband_name", ""))
                    render_confidence("father_husband_name")

                    st.markdown("### Location Details")
                    c1, c2, c3 = st.columns(3)
                    form_data["village"] = c1.text_input("Village (ગામ)", value=data.get("village", ""))
                    render_confidence("village", c1)
                    form_data["taluka"] = c2.text_input("Taluka (તાલુકો)", value=data.get("taluka", ""))
                    render_confidence("taluka", c2)
                    form_data["district"] = c3.text_input("District (જિલ્લો)", value=data.get("district", ""))
                    render_confidence("district", c3)

                    st.markdown("### Property Identification")
                    c4, c5 = st.columns(2)
                    form_data["survey_number"] = c4.text_input("Survey Number", value=data.get("survey_number", ""))
                    render_confidence("survey_number", c4)
                    form_data["plot_block_number"] = c5.text_input("Plot / Block Number", value=data.get("plot_block_number", ""))
                    render_confidence("plot_block_number", c5)

                    st.markdown("### Area & Measurement")
                    c6, c7 = st.columns(2)
                    form_data["area_sq_meter"] = c6.text_input("Area (Sq. Meter)", value=data.get("area_sq_meter", ""))
                    render_confidence("area_sq_meter", c6)
                    
                    extracted_sqft = data.get("area_sq_feet", "")
                    if form_data["area_sq_meter"] and not extracted_sqft:
                        calculated_sqft = convert_sqm_to_sqft(form_data["area_sq_meter"])
                        form_data["area_sq_feet"] = c7.text_input("Area (Sq. Feet)", value=str(calculated_sqft) if calculated_sqft else "")
                    else:
                        form_data["area_sq_feet"] = c7.text_input("Area (Sq. Feet)", value=extracted_sqft)
                    render_confidence("area_sq_feet", c7)

                    st.markdown("### Document Information")
                    c8, c9, c10 = st.columns(3)
                    form_data["document_number"] = c8.text_input("Document Number", value=data.get("document_number", ""))
                    render_confidence("document_number", c8)
                    form_data["registration_date"] = c9.text_input("Registration Date", value=data.get("registration_date", ""))
                    render_confidence("registration_date", c9)
                    form_data["sub_registrar_office"] = c10.text_input("Sub-Registrar Office", value=data.get("sub_registrar_office", ""))
                    render_confidence("sub_registrar_office", c10)

                    st.markdown("### Boundary Details")
                    b1, b2 = st.columns(2)
                    form_data["boundary_east"] = b1.text_area("East (પૂર્વ)", value=data.get("boundary_east", ""))
                    render_confidence("boundary_east", b1)
                    form_data["boundary_west"] = b2.text_area("West (પશ્ચિમ)", value=data.get("boundary_west", ""))
                    render_confidence("boundary_west", b2)
                    b3, b4 = st.columns(2)
                    form_data["boundary_north"] = b3.text_area("North (ઉત્તર)", value=data.get("boundary_north", ""))
                    render_confidence("boundary_north", b3)
                    form_data["boundary_south"] = b4.text_area("South (દક્ષિણ)", value=data.get("boundary_south", ""))
                    render_confidence("boundary_south", b4)
                    
                    form_area_val = form_data["area_sq_feet"]

        
                if st.form_submit_button("Confirm & Save"):
                    # Recalculate estimated value based on form's area, handling different formats
                    try:
                        # Attempt to parse whatever area field is used for the current document type
                        final_area_val = None
                        if document_type == "7/12 Extract (Satbara)":
                            parsed_hectare = parse_hectare_are_sqm(form_area_val)
                            if parsed_hectare is not None:
                                final_area_val = parsed_hectare
                                
                        if final_area_val is None:
                            final_area_val = extract_numeric_value(form_area_val)
                            
                        if final_area_val > 0 and document_type != "Dastavej (Sale Deed)" and document_type != "Index-II":
                            final_area_val = final_area_val * 10.7639
                    except:
                        final_area_val = 0.0
                        
                    final_base_value = final_area_val * rate_per_sqft
                    final_estimated_value = final_base_value * (1.0 - depreciation_pct)

                    # Update form_data with valuation numbers
                    form_data["rate_per_sqft"] = rate_per_sqft
                    form_data["property_age_years"] = property_age_years
                    form_data["estimated_value"] = f"₹ {final_estimated_value:,.2f}"

                    st.session_state.final_data = form_data
                    st.success("Form data validated! You can now download reports.")

            if 'final_data' in st.session_state:
                st.markdown("---")
                st.subheader("📥 Download Options")
                d1, d2 = st.columns(2)
                
                final_data = st.session_state.final_data
                
                # determine the correct file identifier based on document type
                if document_type == "7/12 Extract (Satbara)":
                    file_id = final_data.get("survey_number")
                elif document_type == "Property Card":
                    file_id = final_data.get("city_survey_number")
                else:
                    file_id = final_data.get("document_number")
                    
                if not file_id:
                    file_id = "record"
                
                # make an excel file
                excel_data = generate_excel(final_data)
                d1.download_button(
                    label="Download Excel (.xlsx)",
                    data=excel_data,
                    file_name=f"Valuation_{file_id}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
                # make a pdf report
                pdf_data = generate_pdf_report(final_data)
                d2.download_button(
                    label="Download PDF Report",
                    data=pdf_data,
                    file_name=f"Valuation_{file_id}.pdf",
                    mime="application/pdf"
                )

        # button to reset
        if st.button("🔄 Process Another Document"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

        # Disable Google Chrome Autofill using a hidden JavaScript component
        import streamlit.components.v1 as components
        components.html(
            """
            <script>
                const inputs = window.parent.document.querySelectorAll('input[type="text"]');
                inputs.forEach(input => {
                    input.setAttribute('autocomplete', 'new-password');
                    input.setAttribute('data-form-type', 'other');
                });
            </script>
            """,
            height=0,
            width=0,
        )
