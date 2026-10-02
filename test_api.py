import requests

domain = "google.com"
url = f"https://crt.sh/?q=%.{domain}&output=json"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Response length: {len(response.text)}")
    print(f"First 500 chars:\n{response.text[:500]}")
except Exception as e:
    print(f"Error: {e}")