import json
import time
import openai

CHATGPT_API_KEY = "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"

openai.api_key = CHATGPT_API_KEY

def chatgpt_response(prompt):
    response = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages = [{"role": "user", "content": prompt}],
        temperature =  1,
    )
    response_dict = response.get("choices")
    if response_dict and len(response_dict) > 0:
        promt_response = response_dict[0]["message"]["content"]
    
    print(promt_response)
    return promt_response

crops = ['rice', 'maize', 'chickpea', 'kidneybeans', 'pigeonpeas',
       'mothbeans', 'mungbean', 'blackgram', 'lentil', 'pomegranate',
       'banana', 'mango', 'grapes', 'watermelon', 'muskmelon', 'apple',
       'orange', 'papaya', 'coconut', 'cotton', 'jute', 'coffee']

k = 3
dictionary = {'Name': 'How To Grow?'}
for crop in crops:
    while(k == 0):
        print("This prints once a minute because of 3 RPM")
        time.sleep(60)
        k = 3
    promt = f'How to grow {crop} step-by-step?'
    response = chatgpt_response(promt)
    dictionary[f'{crop}'] = response
    k -= 1
    
# Serializing json
json_object = json.dumps(dictionary, indent=4)
 
# Writing to sample.json
with open("sample.json", "w") as outfile:
    outfile.write(json_object)