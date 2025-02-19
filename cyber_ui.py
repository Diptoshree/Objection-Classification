import streamlit as st
import pandas as pd
import requests
import time
from io import BytesIO

# Django API endpoint
API_URL = "http://127.0.0.1:8000/home/"  # Update this with your actual API URL

st.set_page_config(page_title="Cyber Tehsil Objection Classification Utility", layout="wide")

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Batch Processing (Excel)", "Single Objection Processing"])

# ------------------ PAGE 1: BATCH PROCESSING ------------------
if page == "Batch Processing (Excel)":
    st.title("Batch Objection Processing")
    
    uploaded_file = st.file_uploader("Upload an Excel File with 'Objection' Column", type=["xlsx"])

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

                    # Send request to API
                    response = requests.post(API_URL, json={"objection_text": objection_text})

                    if response.status_code == 200:
                        result = response.json()
                        explanation = result.get("Explanation", "N/A")
                        classification = result.get("Classification", "N/A")
                    else:
                        explanation, classification = "Error in processing", "N/A"

                    results.append([objection_text, explanation, classification])
                    progress_bar.progress((index + 1) / len(df))

                    time.sleep(0.5)  # Simulate processing delay

                # Create DataFrame
                processed_df = pd.DataFrame(results, columns=["Objection", "Explanation", "Classification"])
                st.write("### Processed Data:", processed_df.head())

                # Convert DataFrame to Excel for download
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
    st.title("Single Objection Processing")

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

