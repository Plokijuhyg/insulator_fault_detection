import time
from duckduckgo_search import DDGS

def search_companies_web(query, max_results=3):
    results = []
    with DDGS() as ddgs:
        search_results = ddgs.text(query + " supplier", max_results=max_results)
        for r in search_results:
            results.append({
                "name": r.get("title"),
                "description": r.get("body"),
                "url": r.get("href")
            })
            time.sleep(1)  # تأخير 1 ثانية بين كل نتيجة (تقليل الضغط)
    return results