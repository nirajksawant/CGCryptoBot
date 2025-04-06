import requests

DEX_SCREENER_API_URL = "https://api.dexscreener.com/latest/dex/search/?q=boost"


response = requests.get(DEX_SCREENER_API_URL)
if response.status_code == 200:
    print("Dex Screener API Response:", response.json())  # Print full JSON response
else:
    print(f"Error: {response.status_code}")
