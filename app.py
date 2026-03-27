import streamlit as st  
import base64         
from extraction_engine import extract_structured_data  
from utils import convert_sqm_to_sqft, generate_excel, generate_pdf_report  
import hashlib       

st.set_page_config(page_title="Gujarati Dastavej AI Valuator", layout="wide")

st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa; /* light grey */
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #007bff; /* blue */
        color: white;
    }
    .stForm {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); /* shadow */
    }
    h1, h2, h3 {
        color: #343a40; /* dark grey */
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📄 Gujarati Dastavej AI Valuator")
st.markdown("Extract structured data from property documents and auto-fill valuation forms.")


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
    # let user pick a pdf
    uploaded_file = st.file_uploader("Upload Gujarati Dastavej (PDF)", type=["pdf"])

    if uploaded_file is not None:
        # get the pdf bytes
        uploaded_pdf_bytes = uploaded_file.getvalue()
        
        # make a unique id for this file based on its content
        file_hash = hashlib.sha256(uploaded_pdf_bytes).hexdigest()
        
        # if its a different file, clear the old stuff
        if st.session_state.get("last_uploaded_file_hash") != file_hash:
            st.session_state.pop("extracted_data", None)
            st.session_state.pop("final_data", None)
            st.session_state.last_uploaded_file_hash = file_hash

        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("PDF Preview")
            # convert pdf bytes to base64 so browser can show it
            base64_pdf = base64.b64encode(uploaded_pdf_bytes).decode('utf-8')
            # embed the pdf in the page
            pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf">'
            st.markdown(pdf_display, unsafe_allow_html=True)

        with col2:
            st.subheader("Extracted Details & Form")
            
            # first time? run the ai to extract data
            if 'extracted_data' not in st.session_state:
                with st.spinner("AI is analyzing the document... This may take a moment."):
                    try:
                        # call to the extraction engine to get the data
                        extracted_data = extract_structured_data(api_key, uploaded_pdf_bytes)
                        if "error" in extracted_data:
                            st.error(extracted_data["error"])
                            st.stop()

                        st.session_state.extracted_data = extracted_data
                        st.success("Data extracted successfully!")
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")
                        st.stop()
            

            data = st.session_state.extracted_data

        
            with st.form("valuation_form"):
                st.markdown("### 👤 Owner Details")
                owner_name = st.text_input("Owner Name (માલિકનું નામ)", value=data.get("owner_name", ""))
                father_husband_name = st.text_input("Father / Husband Name (પિતા અથવા પતિનું નામ)", value=data.get("father_husband_name", ""))

                st.markdown("### 📍 Location Details")
                c1, c2, c3 = st.columns(3)
                village = c1.text_input("Village (ગામ)", value=data.get("village", ""))
                taluka = c2.text_input("Taluka (તાલુકો)", value=data.get("taluka", ""))
                district = c3.text_input("District (જિલ્લો)", value=data.get("district", ""))

                st.markdown("### 🏠 Property Identification")
                c4, c5 = st.columns(2)
                survey_num = c4.text_input("Survey Number", value=data.get("survey_number", ""))
                plot_num = c5.text_input("Plot / Block Number", value=data.get("plot_block_number", ""))

                st.markdown("### 📏 Area & Measurement")
                c6, c7 = st.columns(2)
                area_sqm = c6.text_input("Area (Sq. Meter)", value=data.get("area_sq_meter", ""))
                
  
                extracted_sqft = data.get("area_sq_feet", "")
                if area_sqm and not extracted_sqft:
                    calculated_sqft = convert_sqm_to_sqft(area_sqm)
                    area_sqft = c7.text_input("Area (Sq. Feet)", value=str(calculated_sqft) if calculated_sqft else "")
                else:
                    area_sqft = c7.text_input("Area (Sq. Feet)", value=extracted_sqft)

                st.markdown("### 📄 Document Information")
                c8, c9, c10 = st.columns(3)
                doc_num = c8.text_input("Document Number", value=data.get("document_number", ""))
                reg_date = c9.text_input("Registration Date", value=data.get("registration_date", ""))
                registrar = c10.text_input("Sub-Registrar Office", value=data.get("sub_registrar_office", ""))

                st.markdown("### 🗺️ Boundary Details")
                b1, b2 = st.columns(2)
                east = b1.text_area("East (પૂર્વ)", value=data.get("boundary_east", ""))
                west = b2.text_area("West (પશ્ચિમ)", value=data.get("boundary_west", ""))
                b3, b4 = st.columns(2)
                north = b3.text_area("North (ઉત્તર)", value=data.get("boundary_north", ""))
                south = b4.text_area("South (દક્ષિણ)", value=data.get("boundary_south", ""))

        
                if st.form_submit_button("Confirm & Save"):
                    st.session_state.final_data = {
                        "owner_name": owner_name,
                        "father_husband_name": father_husband_name,
                        "village": village,
                        "taluka": taluka,
                        "district": district,
                        "survey_number": survey_num,
                        "plot_block_number": plot_num,
                        "area_sq_meter": area_sqm,
                        "area_sq_feet": area_sqft,
                        "document_number": doc_num,
                        "registration_date": reg_date,
                        "sub_registrar_office": registrar,
                        "boundary_east": east,
                        "boundary_west": west,
                        "boundary_north": north,
                        "boundary_south": south
                    }
                    st.success("Form data validated! You can now download reports.")

            if 'final_data' in st.session_state:
                st.markdown("---")
                st.subheader("📥 Download Options")
                d1, d2 = st.columns(2)
                
                final_data = st.session_state.final_data
                
                # make an excel file
                excel_data = generate_excel(final_data)
                d1.download_button(
                    label="Download Excel (.xlsx)",
                    data=excel_data,
                    file_name=f"Valuation_{final_data['document_number']}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
                # make a pdf report
                pdf_data = generate_pdf_report(final_data)
                d2.download_button(
                    label="Download PDF Report",
                    data=pdf_data,
                    file_name=f"Valuation_{final_data['document_number']}.pdf",
                    mime="application/pdf"
                )

        # button to reset
        if st.button("🔄 Process Another Document"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
