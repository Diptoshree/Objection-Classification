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

# # Load API Key from environment variable
# load_dotenv()
# api_key = os.getenv("OPENAI_API_KEY")
# print(api_key)
# client = OpenAI(api_key=api_key)
# print(client)
# Load API Key from Streamlit Secrets

api_key = st.secrets["secret_section"]["OPENAI_API_KEY"]
# Initialize OpenAI Client
client = OpenAI(api_key=api_key)

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
6. Financial Dispute

The statements may be in English, Hindi, or Hinglish (Hindi written using English phonetics).

Your task is to determine whether a statement indicates an objection and classify it into one of the two categories:

Categories:
Valid Objection: If the statement contains an objection in the above 6 categories .
No Objection: If the statement does not indicate any objection in the above 6 categories .

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
Case 2 (Exception): If the statement implies "no objection" (e.g., "आपत्ति नहीं", "no objection"), classify it as "No Objection".

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
        print('request received')
        data = json.loads(request.body.decode('utf-8'))
        objection_text = data.get("objection_text")
        if not objection_text:
            return JsonResponse({'error': 'No objection text provided'}, status=400)

        # Normalize the objection text
        objection_new = normalize_text(objection_text)
        print(objection_new)
        # Define trigger keywords (including possible spelling variants)
        trigger_words = ['आपत्ति', "आपत्ति", "आपत्ति ", 'आपत्‍ती', "apatati", "aapatti", "aapaati", "appati", "apatti", "apti",
                         "रोक", "बंजर", "लौलाश", "पैतृक", "अन्‍य", "पैतरक", "भुमि","भूमि", "जमीन", "विवाद", "फर्जी", "नामांतरण","अपराध","आराजी","सहमति नहीं",
                         "बाबद्", "विवाद", "अवरोध", "विवादित", "आवश्यक", "सरकारी", "शासकीय", "धोखेबाजी", "कब्‍जा","शासन","आराजियों","अपील",
                         "naksha", "सिविल", "पूर्वजों", "mere", "mera", "case", "civil", "court", "bhumi", "land", "meri",
                         "bandhak", "attached", "namantran", "illegal", "legal", "अवैध", "galat", "registry", "registration",
                         "rasta", "nisast", "निरस्त", "avedan", "appeal", "धोखा-दाड़ी", "धोखा", "fraud", "नक्‍शा", "तरमीम", "वसीयत",]

        # Check for explicit "no objection" phrases
        no_objection_phrases = ['no objection', 'आपत्ति नहीं','dont have objection','dont have any objection','apatti nehi','आपत्ति नहि']

        # Check if any no objection phrase is in the normalized text
        if any(phrase in objection_new for phrase in no_objection_phrases):
            response_data = {
                'Objection Text': objection_text,
                'Explanation': "The statement explicitly mentions 'no objection'.",
                'Classification': "No Objection"
            }
            print("phrase found")
            return JsonResponse(response_data)
        elif any(word in objection_new for word in trigger_words):
            # Check if any keyword exists in the objection text
            found_keyword = None
            for word in trigger_words:
                if word in objection_new:
                    found_keyword = word
                    response_data = {
                        'Objection Text': objection_text,
                        'Explanation': f"The statement contains the keyword '{found_keyword}', indicating an objection related to land/property matters.",
                        'Classification': "Valid Objection"
                    }
                    print("word found")
                    return JsonResponse(response_data)   
        elif reason(objection_new) in ['All Special Characters', 'Number and Special Characters', 'Small word']: 
            reason_text=reason(objection_new)
            response_data = {
                'Objection Text': objection_text,
                'Explanation': reason_text,
                'Classification': "No Objection"
            }
            print("charected found")
            return JsonResponse(response_data)       
        else:
            print("AI processing started")
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
