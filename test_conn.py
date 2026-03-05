import requests
try:
    print("Testing http://127.0.0.1:8000 ...")
    r = requests.get("http://127.0.0.1:8000", timeout=5)
    print(f"Status: {r.status_code}")
    print(f"URL: {r.url}")
    print("Success!")
except Exception as e:
    print(f"Failed: {e}")
