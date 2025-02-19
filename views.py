# from django.shortcuts import render
# from django.http import HttpResponse
# import pandas as pd
# from io import BytesIO
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt

# import pandas as pd
# import openpyxl
# import re
# from openai import OpenAI, AzureOpenAI
# import os
# from dotenv import load_dotenv
# import ssl
# import certifi
# import streamlit as st
# from io import BytesIO
# from langchain_ollama import ChatOllama
# import json
# import openai
# llm=ChatOllama(model='llama3', base_url='http://localhost:11434')
# #import regex as re

# # Load API Key from environment variable
# load_dotenv()

# api_key = os.getenv("OPENAI_API_KEY")
# print(api_key)
# client = OpenAI(api_key=api_key)
# print(client)


# # Function to normalize text
# def normalize_text(text):
#     text = str(text).strip().lower()
#     text = re.sub(r'\s+', ' ', text)
#     text = re.sub(r'\u200b|\u200c', '', text)
#     return text

# # Mapping for valid and invalid objections
# def map_remark_to_final(remark):
#     if remark == 'Words related to Objection' or remark == 'More than 15 characters' or remark == 'Objection' :
#         return 'Objection'
#     elif remark == 'All Special Characters'  or remark == 'Number and Special Characters' or remark == 'Long word'or remark == 'Small word':
#         return 'No Objection'

# # Function to count words
# def count_words(text):
#     return len(text.split())

# # Function to find maximum word length
# def max_word_length(text):
#     words = text.split()
#     return max(len(word) for word in words) if words else 0

# # Reason function
# def reason(Objection_new):
#     Objection = normalize_text(Objection_new)
#     word_count = count_words(Objection_new)
#     max_word_len = max_word_length(Objection_new)

#     if re.fullmatch(r'[^a-zA-Z0-9\s]+', Objection_new):
#         return 'All Special Characters'
    
#     if re.fullmatch(r'[^a-zA-Z\s]+', Objection_new):
#         return 'Number and Special Characters'
    
#     if len(Objection) > 15 and re.search(r'[a-zA-Zअ-हऒ-௽०-९\s]', Objection_new):
#         return 'More than 15 characters' 
    
#     if len(Objection) < 5 and re.search(r'[a-zA-Zअ-हऒ-௽०-९\s]', Objection_new):
#         return 'Small word'
    
#     if word_count == 1 and max_word_len > 15:
#         return 'Long word'
    
#     return 'Objection'

# def categorize_statement_openai(objection_text):
#     try:
#         print("Connecting to OpenAI")
#         # Send request to the OpenAI API
#         messages=[
#                     {
#                         "role": "system",
#                         "content": f"""
#                         You are a helpful AIassistant specializing in categorizing statements (referred to as {objection_text}) that may indicate objections related to: 
#                         1.Sale of land property
#                         2.Map modification (Naksha Tarmeem)
#                         3.Name change (Namantaran)
#                         4.Government land-related matters
#                         5.Court related matter
#                         The statements may be in English, Hindi, or Hinglish (Hindi written using English phonetics).

#                         Your task is to determine whether a statement indicates an objection and classify it into one of the two categories:

#                         Categories:
#                         Valid Objection: If the statement contains an objection.
#                         No Objection: If the statement does not indicate any objection.
#                         Classification Process (Sequential Steps):
#                         Step 1: Keyword Detection (Primary Step)
#                         Check if the statement contains any of the following keywords (including possible spelling mistakes or incomplete words):
#                         ['आपत्ति', "आपत्ति", "आपत्ति ", 'आपत्‍ती', "apatati", "aapatti", "aapaati", "appati", "apatti", "apti",
#                         "रोक", "बंजर", "लौलाश", "पैतृक", "अन्‍य", "पैतरक", "भुमि", "जमीन", "विवाद", "फर्जी", "नामांतरण",
#                         "बाबद्", "विवाद", "अवरोध", "विवादित", "आवश्यक", "सरकारी","शासकीय", "धोखेबाजी", "कब्‍जा", "जमीन", "naksha",
#                         "सिविल", "पूर्वजों", "mere", "mera", "case", "civil", "court", "bhumi", "land", "meri", "bandhak",
#                         "attached", "namantran", "illegal", "legal", "अवैध", "galat", "registry", "registration", "rasta",
#                         "nisast", "निरस्त", "avedan", "appeal", "धोखा-दाड़ी", "धोखा", "fraud", "नक्‍शा", "तरमीम", "वसीयत"]

#                         Case 1: If a keyword is found, strictly classify it as "Valid Objection".

#                         Case 2 (Exception): If the statement explicitly mentions “no objection” (e.g., "आपत्ति नहीं", "no objection"), classify it as "No Objection".

#                         If a keyword is found, stop here and do not proceed to Step 2.

#                         Step 2: If No Keyword is Found (Secondary Step)
#                         Case 3: If the statement is not meaningful and contains no keyword, classify it as "No Objection".
#                         Case 4: If the statement is meaningful but does not contain any keyword, analyze the intent:
#                         If it expresses concerns about land disputes, legal issues, ownership conflicts, or government restrictions, classify it as "Valid Objection".
#                         Otherwise, classify it as "No Objection".
#                         For each statement, please provide the response in the following json format:
                        
#                         {{
#                             "Objection Statement": "{objection_text}",
#                             "Explanation": "Provide a clear and concise explanation for your classification. Your explanation should justify why the statement falls into the chosen category.",
#                             "Classification": "Classify the statement into one of the two categories: 'Valid Objection' or  'No Objection'."
#                         }}
#                         **Important: Strictly do not provide any additional information or explanation outside the defined format.**
                                    
#                         Example1:
#                         {{
#                             "Objection Statement": "अभी तक किसी भी तरह से जानकारी नहीं मिली",
#                             "Explanation": "The statement indicates a lack of awareness about the property transaction. Since no objection to the sale is mentioned, this statement is classified as No Objection.",
#                             "Classification": "No Objection"
#                         }}
                                    
#                         Example2:
#                         {{         
#                             "Objection Statement": "namantaran nirast kare",
#                             "Explanation": "This statement directly requests the cancellation of a property transfer (Namantaran), making it a valid objection to the sale.",
#                             "Classification": "Valid Objection"
#                         }}
                                    
#                         Example3:
#                         {{
#                             "Objection Statement": "main bhi unka beta hun mere ko bhi hissa chahie",
#                             "Explanation": "This is a family dispute regarding the share of land. The individual is requesting a share of the land, indicating an objection to the sale or division.",
#                             "Classification": "Valid Objection"
#                         }}
                                    
#                         Example4:
#                         {{
#                             "Objection Statement": "I have received a notice on a text message on my mobile number",
#                             "Explanation": "This statement mentions receiving a notice but does not explicitly indicate any objection to the property sale. Therefore, it is classified as No Objection.",
#                             "RClassification": "No Objection"
#                         }}
#                         ***Make sure there is no mistake in making json structure
#                         """
#                     },
#                     {
#                         "role": "user",
#                         "content": objection_text
                            
                        
#                     }
#                 ]
#             # print(messages)
#         try:
#             response = client.chat.completions.create(
#                 model="gpt-4o-mini",
#                 messages=messages            )
#             print(response)
#         except openai.OpenAIError as e:
#             print(f"OpenAI API error: {e}")
        
    
#         print("AI response....",response)
        

#         # Parse response
#         result = response.choices[0].message.content.strip()  # Corrected response parsing
#         print("Extracted result....",result)
        
#         # Convert JSON response to dictionary
#         if isinstance(result, str):
#             data = json.loads(result)  # Parse string into JSON
#         else:
#             data = result  # Already a dictionary
        
#         print("Processing the response...")
        
#         # Extracting components
#         objection_part=data["Objection Statement"]
#         explanation_part = data["Explanation"]
#         result_classification = data["Classification"]

#         # Print each part for debugging purposes
#         print("Objection Part:", objection_part)
#         print("Explanation Part:", explanation_part)
#         print("Result Classification:", result_classification)

#         return objection_part, explanation_part, result_classification

#     except Exception as e:
#         print(f"Error occurred: {str(e)}")
    
#         #  Retry mechanism (instead of recursion)
#         for _ in range(2):  # Retry up to 2 times
#             try:
#                 return categorize_statement_openai(objection_text)
#             except Exception as retry_error:
#                 print(f"Retry failed: {str(retry_error)}")
#         return None, None, None  # Return None if all retries fail
    
#     # except Exception as e:
#     #     print(f"Error occurred: {str(e)}")
#     #     return None, None, None

    
# @csrf_exempt
# def home(request):
#     if request.method == 'POST':
#         data = json.loads(request.body.decode('utf-8'))
#         # full_url = request.build_absolute_uri()
#         # return HttpResponse(f"Full URL: {full_url}")
#         objection_text = data.get("objection_text")
#         if not objection_text:
#             return JsonResponse({'error': 'No objection text provided'}, status=400)

#         # Normalize the objection text
#         objection_new = normalize_text(objection_text)
        
#         # trigger_words = ['आपत्ति', "आपत्ति", "आपत्ति ", 'आपत्‍ती', "apatati", "aapatti", "aapaati", "appati","apatti","apti",
#         #                  "रोक", "बंजर", "लौलाश", "पैतृक", "अन्‍य", "पैतरक", "भुमि", "जमीन", "विवाद", 
#         #                  "फर्जी", "नामांतरण", "बाबद्", "विवाद", "अवरोध", "विवादित", "आवश्यक", "सरकारी", 
#         #                  "धोखेबाजी", "कब्‍जा", "जमीन", "naksha", "सिविल", "पूर्वजों", "mere", "mera", "case", 
#         #                  "civil", "court", "bhumi", "meri", "bandhak", "attached", "namantran", "illegal", 
#         #                  "legal", "अवैध", "galat", "registry", "registration", "rasta"]

#         # trigger_word_found = next((word for word in trigger_words if word in objection_new), None)
#         # # 
#         reason_text = reason(objection_new)
#         if reason_text in ['All Special Characters', 'Number and Special Characters', 'Small word']:
#             explanation = reason_text
#             classification = "No Objection"
#         else:
#             _, explanation, classification = categorize_statement_openai(objection_new)
         
#         response_data = {
#             'Objection Text': objection_text,
#             'Explanation': explanation,
#             'Classification': classification
#         }
#         return JsonResponse(response_data)
    
#     return render(request, 'objection_form.html')

# ######zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import re
import os
from io import BytesIO
from dotenv import load_dotenv

import openai
from openai import OpenAI, AzureOpenAI
from langchain_ollama import ChatOllama

# Initialize ChatOllama (if needed)
llm = ChatOllama(model='llama3', base_url='http://localhost:11434')

# Load API Key from environment variable
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
print(api_key)
client = OpenAI(api_key=api_key)
print(client)

# Function to normalize text
def normalize_text(text):
    text = str(text).strip().lower()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\u200b|\u200c', '', text)
    return text

# Mapping for valid and invalid objections (if needed)
def map_remark_to_final(remark):
    if remark in ['Words related to Objection', 'More than 15 characters', 'Objection']:
        return 'Objection'
    elif remark in ['All Special Characters', 'Number and Special Characters', 'Long word', 'Small word']:
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

# Function to call OpenAI for categorization if needed
def categorize_statement_openai(objection_text):
    try:
        print("Connecting to OpenAI")
        # Send request to the OpenAI API with a detailed system message
        messages = [
            {
                "role": "system",
                "content": f"""
You are a helpful AI assistant specializing in categorizing statements (referred to as the objection text) that may indicate objections related to: 
1. Sale of land property
2. Map modification (Naksha Tarmeem)
3. Name change (Namantaran)
4. Government land-related matters
5. Court related matter

The statements may be in English, Hindi, or Hinglish (Hindi written using English phonetics).

Your task is to determine whether a statement indicates an objection and classify it into one of the two categories:

Categories:
Valid Objection: If the statement contains an objection.
No Objection: If the statement does not indicate any objection.

Classification Process (Sequential Steps):
Step 1: Keyword Detection (Primary Step)
Check if the statement contains any of the following keywords (including possible spelling mistakes or incomplete words):
['आपत्ति', "आपत्ति", "आपत्ति ", 'आपत्‍ती', "apatati", "aapatti", "aapaati", "appati", "apatti", "apti",
"रोक", "बंजर", "लौलाश", "पैतृक", "अन्‍य", "पैतरक", "भुमि", "जमीन", "विवाद", "फर्जी", "नामांतरण",
"बाबद्", "विवाद", "अवरोध", "विवादित", "आवश्यक", "सरकारी", "शासकीय", "धोखेबाजी", "कब्‍जा", "जमीन",
"naksha", "सिविल", "पूर्वजों", "mere", "mera", "case", "civil", "court", "bhumi", "land", "meri", "bandhak",
"attached", "namantran", "illegal", "legal", "अवैध", "galat", "registry", "registration", "rasta",
"nisast", "निरस्त", "avedan", "appeal", "धोखा-दाड़ी", "धोखा", "fraud", "नक्‍शा", "तरमीम", "वसीयत"]

Case 1: If a keyword is found, strictly classify it as "Valid Objection" and do not analyze intent further.
Case 2 (Exception): If the statement explicitly mentions "no objection" (e.g., "आपत्ति नहीं", "no objection"), classify it as "No Objection".

Stop processing after Step 1 if a keyword is detected.

Step 2: If no keyword is found:
Case 3: If the statement is not meaningful and contains no keyword, classify as "No Objection".
Case 4: If the statement is meaningful but does not contain any keyword, analyze the intent:
      If it expresses concerns about land disputes, legal issues, ownership conflicts, or government restrictions, classify as "Valid Objection".
      Otherwise, classify as "No Objection".

Return the result in the following JSON format:
{{
    "Objection Statement": "{objection_text}",
    "Explanation": "Provide a clear and concise explanation for your classification. Your explanation should justify why the statement falls into the chosen category.",
    "Classification": "Classify the statement into one of the two categories: 'Valid Objection' or 'No Objection'."
}}
**Important: Strictly do not provide any additional information or explanation outside the defined format.**
                """
            },
            {
                "role": "user",
                "content": objection_text
            }
        ]
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages
            )
            print("Raw OpenAI Response:", response)
        except openai.OpenAIError as e:
            print(f"OpenAI API error: {e}")
            return None, None, None

        result = response.choices[0].message.content.strip()
        print("Extracted result:", result)
        
        # Attempt to parse JSON from the response
        try:
            data = json.loads(result)
        except json.JSONDecodeError:
            print("JSON Parsing Error. Raw Response:", result)
            return None, None, None
        
        print("Processing the response...")
        objection_part = data.get("Objection Statement", "")
        explanation_part = data.get("Explanation", "")
        result_classification = data.get("Classification", "")

        print("Objection Part:", objection_part)
        print("Explanation Part:", explanation_part)
        print("Result Classification:", result_classification)

        return objection_part, explanation_part, result_classification

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        # Retry mechanism (retry up to 2 times)
        for _ in range(2):
            try:
                return categorize_statement_openai(objection_text)
            except Exception as retry_error:
                print(f"Retry failed: {str(retry_error)}")
        return None, None, None

@csrf_exempt
def home(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        objection_text = data.get("objection_text")
        if not objection_text:
            return JsonResponse({'error': 'No objection text provided'}, status=400)

        # Normalize the objection text
        objection_new = normalize_text(objection_text)

        # Define trigger keywords (including possible spelling variants)
        trigger_words = ['आपत्ति', "आपत्ति", "आपत्ति ", 'आपत्‍ती', "apatati", "aapatti", "aapaati", "appati", "apatti", "apti",
                         "रोक", "बंजर", "लौलाश", "पैतृक", "अन्‍य", "पैतरक", "भुमि", "जमीन", "विवाद", "फर्जी", "नामांतरण","अपराध","आराजी","सहमति नहीं",
                         "बाबद्", "विवाद", "अवरोध", "विवादित", "आवश्यक", "सरकारी", "शासकीय", "धोखेबाजी", "कब्‍जा","शासन","आराजियों","अपील",
                         "naksha", "सिविल", "पूर्वजों", "mere", "mera", "case", "civil", "court", "bhumi", "land", "meri",
                         "bandhak", "attached", "namantran", "illegal", "legal", "अवैध", "galat", "registry", "registration",
                         "rasta", "nisast", "निरस्त", "avedan", "appeal", "धोखा-दाड़ी", "धोखा", "fraud", "नक्‍शा", "तरमीम", "वसीयत",]

        # Check for explicit "no objection" phrases
        no_objection_phrases = ['no objection', 'आपत्ति नहीं','dont have objection','dont have any objection']

        # Check if any no objection phrase is in the normalized text
        if any(phrase in objection_new for phrase in no_objection_phrases):
            response_data = {
                'Objection Text': objection_text,
                'Explanation': "The statement explicitly mentions 'no objection'.",
                'Classification': "No Objection"
            }
            return JsonResponse(response_data)

        # Check if any keyword exists in the objection text
        found_keyword = None
        for word in trigger_words:
            if word in objection_new:
                found_keyword = word
                break

        # If keyword found, classify immediately as Valid Objection
        if found_keyword:
            response_data = {
                'Objection Text': objection_text,
                'Explanation': f"The statement contains the keyword '{found_keyword}' indicating an objection related to land/property matters.",
                'Classification': "Valid Objection"
            }
            return JsonResponse(response_data)

        # If no keyword found, use the reasoning function to decide further
        reason_text = reason(objection_new)
        if reason_text in ['All Special Characters', 'Number and Special Characters', 'Small word']:
            explanation = reason_text
            classification = "No Objection"
        else:
            # Call OpenAI if further analysis is required
            _, explanation, classification = categorize_statement_openai(objection_new)
            # Fallback if OpenAI fails to classify
            if not classification:
                classification = "No Objection"
                explanation = "Unable to determine a valid objection from the provided text."

        response_data = {
            'Objection Text': objection_text,
            'Explanation': explanation,
            'Classification': classification
        }
        return JsonResponse(response_data)
    
    return render(request, 'objection_form.html')
