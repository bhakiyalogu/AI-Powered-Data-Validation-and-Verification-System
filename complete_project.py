import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor

# Define the LLM Foundry token for your API requests
LLMFOUNDRY_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6Im11dGh1a3VtYXIucGFuY2hhYmVrYXNhbkBzdHJhaXZlLmNvbSJ9.uiwWDBAUFxkHaLY4duukUT0h94izwJH6rktK5mksef0"

# Function to interact with the first model
def chat_with_llm_model1(user_input):
    response = requests.post(
        "https://llmfoundry.straive.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {LLMFOUNDRY_TOKEN}:Bhakiya_BOT"},
        json={"model": "gpt-4o-mini", "messages": [{"role": "user", "content": user_input}]}
    )
    response_json = response.json()
    answer = response_json['choices'][0]['message']['content']
    return answer

# Function to interact with the second model
def chat_with_llm_model2(user_input):
    response = requests.post(
        "https://llmfoundry.straive.com/anthropic/v1/messages",
        headers={"Authorization": f"Bearer {LLMFOUNDRY_TOKEN}:Muthu_bot"},
        json={"model": "claude-3-haiku-20240307", "max_tokens": 10, "messages": [{"role": "user", "content": user_input}]},
    )
    
    if response.status_code == 200:
        response_json = response.json()
        # Assuming we correctly retrieve the message
        answer = response_json['content'][0]['text']  # Modify based on the actual response
        return answer
    else:
        return f"Error: {response.status_code} - {response.text}"

# Load the Excel file and the specific sheet
file_path = r'D:\python_test\test\city_name\city_name.xlsx'
sheet_name = 'Cosmo Input Report'
df = pd.read_excel(file_path, sheet_name=sheet_name)

# Load the prompt from the text file
with open(r'D:\python_test\test\city_name\prompt.txt', 'r') as file:
    prompt_template = file.read()

# Check for result columns and add them if they don't exist
for col in ['Result_Model1', 'Result_Model2', 'City_Check']:
    if col not in df.columns:
        df[col] = None

# Function to process each row and update results for both models
def process_row(index, row):
    main_city = row['Source City name']
    description = row['Description']
    prompt = prompt_template.format(main_city=main_city, description=description)
    
    result_model1 = chat_with_llm_model1(prompt)
    result_model2 = chat_with_llm_model2(prompt)
    
    # Check if the city name or its possessive form is in the description
    city_name_lower = main_city.lower()
    description_lower = description.lower()
    city_check = (city_name_lower in description_lower) or (f"{city_name_lower}'s" in description_lower)
    
    city_check_result = "City name available and matching" if city_check else "City name not available or mismatched"
    
    return index, result_model1, result_model2, city_check_result

# Parallel processing of the rows
with ThreadPoolExecutor() as executor:
    futures = {executor.submit(process_row, i, row): i for i, row in df.iterrows()}
    for future in futures:
        i, result_model1, result_model2, city_check_result = future.result()
        df.at[i, 'Result_Model1'] = result_model1
        df.at[i, 'Result_Model2'] = result_model2
        df.at[i, 'City_Check'] = city_check_result

# Save the modified DataFrame back to Excel
df.to_excel(r'D:\python_test\test\city_name\processed_city_name.xlsx', sheet_name=sheet_name, index=False)
