# utils/serper_api.py

import requests

API_KEY = "3bd764937d4fda3f539b38a8debbb778be10a0a8"  # ضع مفتاحك الخاص هنا

def search_companies_web(query, country="Lebanon", local=True, max_results=5):
    try:
        # تحديد موقع البحث بناءً على الخيار
        location_term = country if local else "international"

        data = {
            "q": f"{query} insulator supplier in {location_term}"
        }
        headers = {
            "X-API-KEY": API_KEY,
            "Content-Type": "application/json"
        }
        response = requests.post("https://google.serper.dev/search", json=data, headers=headers)
        response.raise_for_status()

        results = []
        for item in response.json().get("organic", [])[:max_results]:
            results.append({
                "name": item.get("title"),
                "description": item.get("snippet"),
                "url": item.get("link")
            })

        return results

    except Exception as e:
        print("❌ Error during search:", e)
        return []
