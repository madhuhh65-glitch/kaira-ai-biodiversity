import requests
import json
import time

url = "http://127.0.0.1:8000/identify"
data = {"text": "A large predatory cat with a golden mane living in the savanna."}

print("Testing API with new Key...")
try:
    response = requests.post(url, data=data, timeout=30)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("Response Success!")
        print(f"Species: {result.get('species')}")
        print(f"Source: {result.get('source')}")
        if result.get('source') == 'Error':
             print("Wait, source is Error. Details:", result.get('details'))
        else:
             print("API Key validation PASSED.")
    else:
        print("Response Failed!")
        print(response.text)

except Exception as e:
    print(f"Connection Error: {e}")
