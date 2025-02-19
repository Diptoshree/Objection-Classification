import pandas as pd
import openpyxl
import re
from openai import OpenAI
import os
from dotenv import load_dotenv
import ssl
import certifi
import streamlit as st
from io import BytesIO
from langchain_ollama import ChatOllama
import json
llm=ChatOllama(model='llama2', base_url='http://localhost:11434')
#import regex as re

# Function to normalize text
def normalize_text(text):
    text = str(text).strip().lower()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\u200b|\u200c', '', text)
    return text

# Mapping for valid and invalid objections
def map_remark_to_final(remark):
    if remark == 'Words related to Objection' or remark == 'More than 15 characters' or remark == 'Objection' :
        return 'Objection'
    elif remark == 'All Special Characters'  or remark == 'Number and Special Characters' or remark == 'Long word'or remark == 'Small word':
        return 'No Objection'

# Function to count words
def count_words(text):
    return len(text.split())

# Function to find maximum word length
def max_word_length(text):
    words = text.split()
    return max(len(word) for word in words) if words else 0

# Reason function
def reason(Objection_new):
    Objection = normalize_text(Objection_new)
    word_count = count_words(Objection_new)
    max_word_len = max_word_length(Objection_new)

    if re.fullmatch(r'[^a-zA-Z0-9\s]+', Objection_new):
        return 'All Special Characters'
    
    if re.fullmatch(r'[^a-zA-Z\s]+', Objection_new):
        return 'Number and Special Characters'
    
    if len(Objection) > 15 and re.search(r'[a-zA-Zअ-हऒ-௽०-९\s]', Objection_new):
        return 'More than 15 characters' 
    
    if len(Objection) < 5 and re.search(r'[a-zA-Zअ-हऒ-௽०-९\s]', Objection_new):
        return 'Small word'
    
    if word_count == 1 and max_word_len > 15:
        return 'Long word'
    
    return 'Objection'

# Function for categorizing the statement using OpenAI API
def categorize_statement(objection_text):
    try:
        response = llm.invoke(
            [
                {
                    "role": "system",
                    "content": f"""
                    You are a helpful assistant specializing in categorizing statements (referred to as {objection_text}) that may indicate objections related to land property transactions. The statements could be written in English, Hindi, or Hinglish (Hindi written using English phonetics).

                    Your task is to determine whether the statement indicates an objection to the sale of land property and classify the statement into one of the following two categories:

                    1 - Valid Objection:If the statement indicates an objection/Apatti  to the sale of land property
                    2 - No Objection:Any statement that is not a objection or non meaningful text like only special screcter only for example ".........." , ""gygjhjkkjkj hgjhkkhjjlljlhffg gdfhjlklkgfsgghk"
                    
                    For each statement, please provide the response in the following json format:
                    
                    {{
                        "Objection Statement": "{objection_text}",
                        "Explanation": "Provide a clear and concise explanation for your classification. Your explanation should justify why the statement falls into the chosen category.",
                        "Result": "Classify the statement into one of the two categories: 'Valid Objection' or  'No Objection'."
                    }}
                    **Important: Strictly do not provide any additional information or explanation outside the defined format.**
                                
                    Example1:
                    {{
                        "Objection Statement": "अभी तक किसी भी तरह से जानकारी नहीं मिली",
                        "Explanation": "The statement indicates a lack of awareness about the property transaction. Since no objection to the sale is mentioned, this statement is classified as No Objection.",
                        "Result": "No Objection"
                    }}
                                
                    Example2:
                    {{         
                        "Objection Statement": "namantaran nirast kare",
                        "Explanation": "This statement directly requests the cancellation of a property transfer (Namantaran), making it a valid objection to the sale.",
                        "Result": "Valid Objection"
                    }}
                                
                    Example3:
                    {{
                        "Objection Statement": "main bhi unka beta hun mere ko bhi hissa chahie",
                        "Explanation": "This is a family dispute regarding the share of land. The individual is requesting a share of the land, indicating an objection to the sale or division.",
                        "Result": "Valid Objection"
                    }}
                                
                    Example4:
                    {{
                        "Objection Statement": "I have received a notice on a text message on my mobile number",
                        "Explanation": "This statement mentions receiving a notice but does not explicitly indicate any objection to the property sale. Therefore, it is classified as No Objection.",
                        "Result": "No Objection"
                    }}
                    ***Make sure there is no mistake in making json structure
                    """

                },
                {
                    "role": "user",
                    "content": f"Categorize the following objection statement and explain why: '{objection_text}'"
                }
            ]
        )

        result = response#.content  # Ensure 'response' contains a dictionary with a 'content' key

        print("............................")
        print("AI Response:", result)

        
        print("Processing the response...")


        data = json.loads(result.content)
        # Extracting components
        #objection_part = result.split('"Objection Statement":')[1].split(',"Explanation":')[0].strip().strip#('"')
        objection_part=data["Objection Statement"]
        explanation_part = data["Explanation"]
        result_classification = data["Result"]

        # Print each part for debugging purposes
        print("Objection Part:", objection_part)
        print("Explanation Part:", explanation_part)
        print("Result Classification:", result_classification)

        return objection_part, explanation_part, result_classification


    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return None, None, None
