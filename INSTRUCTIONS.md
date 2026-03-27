# 📄 Gujarati Dastavej AI Valuator - A to Z Guide

## 🌟 Overview
The **Gujarati Dastavej AI Valuator** is a powerful automation tool designed to extract structured data from Gujarati property documents (Dastavej) and assist in property valuation. It uses Google's **Gemini 1.5 Flash** AI to read scanned PDFs and automatically fill out valuation forms.

---

## 🚀 How to Run the Project

### 1️⃣ Prerequisites
- **Python**: Version 3.10 or higher.
- **Gemini API Key**: You need a valid API key from [Google AI Studio](https://aistudio.google.com/).
- **Internet Connection**: Required for AI processing.

### 2️⃣ Installation Steps
1. **Open a Terminal** (PowerShell or Command Prompt).
2. **Navigate to the Project Folder**:
   ```powershell
   cd "c:\Users\Lenovo\OneDrive\Desktop\Sem-5 Vacation\projects\valuation"
   ```
3. **Create a Virtual Environment** (Optional but Recommended):
   ```powershell
   py -m venv venv
   ```
4. **Activate the Virtual Environment**:
   - Windows: `.\venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
5. **Install Dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

### 3️⃣ Running the App
Start the Streamlit application with the following command:
```powershell
streamlit run app.py
```
After running, a new tab will automatically open in your web browser (usually at `http://localhost:8501`).

---

## 🛠️ How to Use the App

1. **Enter API Key**: In the sidebar on the left, paste your **Gemini API Key**.
2. **Upload PDF**: Click on "Browse files" to upload a Gujarati property document (PDF).
3. **Preview & Analyze**:
   - The left side shows a preview of your uploaded PDF.
   - The AI will automatically start analyzing the document.
4. **Verify Extracted Data**:
   - The right side will populate with extracted details like Owner Name, Area, Survey Number, and Boundaries.
   - **Important**: Always review the extracted data and make manually corrections if needed.
5. **Save & Download**:
   - Click **"Confirm & Save"** once the data is correct.
   - Download the finalized data as an **Excel (.xlsx)** or a **PDF Report**.

---

## 📁 Project Structure Explained

- **`app.py`**: The main user interface built with Streamlit.
- **`extraction_engine.py`**: The "brain" of the project. It converts PDF pages into images and sends them to Gemini for data extraction.
- **`utils.py`**: Contains helper functions for unit conversion (Sq. Meter to Sq. Feet) and generating downloadable reports.
- **`requirements.txt`**: List of all necessary libraries.
- **`DemoDastavej.pdf`**: Example documents provided for testing the application.

---

## ⚠️ Important Notes
- **Accuracy**: While Gemini 1.5 Flash is highly accurate, always double-check the extracted values against the original document.
- **Privacy**: Your API key is used only for current session processing and is not stored by the application.
- **Gujarati Support**: The extraction engine is specifically prompted to understand and extract data from Gujarati script.

---
*Created by Antigravity AI*
