import streamlit as st
import pandas as pd
import requests
import time
from io import BytesIO
import base64

# Django API endpoint
API_URL = "http://127.0.0.1:8000/home/"

st.set_page_config(page_title="Cyber Tehsil Objection Classification Utility", layout="wide")

def set_background(image_path):
    """Sets a background image for the entire Streamlit app."""
    with open(image_path, "rb") as img_file:
        base64_image = base64.b64encode(img_file.read()).decode()

    # CSS for background and layout adjustments
    bg_css = f"""
    <style>
    .stApp {{
        background: url("data:image/png;base64,{base64_image}") no-repeat center center fixed;
        background-size: cover;
    }}

    .title-box {{
        background-color: rgba(255, 255, 255, 0.5);
        padding: 5px;
        border-radius: 4px;
        text-align: left;
        width: 70%;
        margin-left: 0%;
        margin-top: 0px;
        margin-bottom: 5px;
        max-height: 80px;
    }}

    .reduce-space {{
        margin-bottom: -20px !important;
    }}

    .file-uploader {{
        background-color: rgba(255, 223, 186, 0.5) !important;
        padding: 10px;
        border-radius: 4px;
        

    .stButton button {{
        background-color: #ffffff !important;
        color: #333333 !important;
        border: 1px solid #333333 !important;
        
    }}
    </style>
    """
    st.markdown(bg_css, unsafe_allow_html=True)

# Set the background image
set_background("a1.jpg")

# Title with White Transparent Box
st.markdown('<div class="title-box"><h1>Cyber Tehsil Objection Classification</h1></div>', unsafe_allow_html=True)

# Navigation (Without Sidebar)
st.markdown('<p class="reduce-space"><b>Choose an option:</b></p>', unsafe_allow_html=True)
page = st.radio("", ["Batch Processing Excel", "Single Objection Processing"])

# ------------------ PAGE 1: BATCH PROCESSING (EXCEL) ------------------
if page == "Batch Processing Excel":
    #st.subheader("Batch Objection Processing")
    
    uploaded_file = st.file_uploader("Upload an Excel File with 'Objection' Column", type=["xlsx"], key="batch_upload")

    if uploaded_file:
        df = pd.read_excel(uploaded_file, engine='openpyxl')
        
        if "Objection" not in df.columns:
            st.error("Uploaded file must have an 'Objection' column.")
        else:
            st.write("### Preview of Uploaded Data:", df.head())

            if st.button("Start Processing"):
                progress_bar = st.progress(0)
                results = []
                
                for index, row in df.iterrows():
                    objection_text = row["Objection"]

                    response = requests.post(API_URL, json={"objection_text": objection_text})

                    if response.status_code == 200:
                        result = response.json()
                        explanation = result.get("Explanation", "N/A")
                        classification = result.get("Classification", "N/A")
                    else:
                        explanation, classification = "Error in processing", "N/A"

                    results.append([objection_text, explanation, classification])
                    progress_bar.progress((index + 1) / len(df))

                    time.sleep(0.5)

                processed_df = pd.DataFrame(results, columns=["Objection", "Explanation", "Classification"])
                st.write("### Processed Data:", processed_df.head())

                output = BytesIO()
                processed_df.to_excel(output, index=False, engine='openpyxl')
                output.seek(0)

                st.download_button(
                    label="Download Processed Excel",
                    data=output,
                    file_name="processed_objections.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

# ------------------ PAGE 2: SINGLE OBJECTION PROCESSING ------------------
if page == "Single Objection Processing":
    #st.subheader("Single Objection Processing")

    objection_text = st.text_area("Enter Objection Text")

    if st.button("Analyze Objection"):
        if objection_text.strip():
            with st.spinner("Processing... Please wait."):
                response = requests.post(API_URL, json={"objection_text": objection_text})

                if response.status_code == 200:
                    result = response.json()
                    explanation = result.get("Explanation", "N/A")
                    classification = result.get("Classification", "N/A")

                    st.success("Processing Completed!")
                    st.write(f"**Explanation:** {explanation}")
                    st.write(f"**Classification:** {classification}")
                else:
                    st.error("Error in API response. Please try again.")
        else:
            st.warning("Please enter an objection text before analyzing.")
