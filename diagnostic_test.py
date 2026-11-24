import requests
import json

claim = "Vaccines reduce the risk of infectious diseases."
response = requests.post(
    "http://127.0.0.1:8000/analyze",
    json={"claim": claim},
    timeout=300
)

print("HTTP STATUS:", response.status_code)
data = response.json()
result = data.get("result", {})

print("\n=== ANALYSIS SUMMARY ===")
print("SUCCESS:", data.get("success"))
print("CLAIM:", result.get("claim"))
print("CATEGORY:", result.get("category"))
print("STATUS:", result.get("status"))
print("RETRIEVED:", result.get("retrieved_articles"))
print("ANALYZED:", result.get("analyzed_articles"))

articles = result.get("articles", [])
print("\nARTICLE COUNT:", len(articles))

for i, article in enumerate(articles[:3], 1):
    sentences = article.get("sentences", [])
    print("\nARTICLE", i)
    print("TITLE:", article.get("title"))
    print("PMID:", article.get("pmid"))
    print("OVERALL COUNTS:", article.get("overall_counts"))
    print("SENTENCE COUNT:", len(sentences))
    for sentence in sentences[:5]:
        print(json.dumps({
            "sentence": sentence.get("sentence"),
            "sentence_type": sentence.get("sentence_type"),
            "evidence_classification": sentence.get("evidence_classification"),
            "relevance": sentence.get("relevance"),
            "confidence": sentence.get("evidence_confidence")
        }, ensure_ascii=False))

print("\n=== SEARCH SUMMARY ===")
print(json.dumps(result.get("search_summary", {}), ensure_ascii=False, indent=2))
