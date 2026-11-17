import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote


class PubMedRetriever:
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

    def __init__(self, max_results=10):
        self.max_results = max_results
        self.session = requests.Session()

    def search_articles(self, query):
        url = self.BASE_URL + "esearch.fcgi"

        params = {
            "db": "pubmed",
            "term": query,
            "retmax": self.max_results,
            "retmode": "json",
            "sort": "relevance"
        }

        response = self.session.get(
            url,
            params=params,
            timeout=20
        )
        response.raise_for_status()

        data = response.json()
        return data["esearchresult"].get("idlist", [])

    def fetch_articles(self, pmids):
        if not pmids:
            return []

        url = self.BASE_URL + "efetch.fcgi"

        params = {
            "db": "pubmed",
            "id": ",".join(pmids),
            "retmode": "xml"
        }

        response = self.session.get(
            url,
            params=params,
            timeout=30
        )
        response.raise_for_status()

        root = ET.fromstring(response.content)
        articles = []

        for article in root.findall(".//PubmedArticle"):
            pmid = article.findtext(".//PMID", default="")

            title_element = article.find(".//ArticleTitle")
            title = "".join(title_element.itertext()) if title_element is not None else ""

            abstract_parts = []

            for abstract_text in article.findall(".//Abstract/AbstractText"):
                text = "".join(abstract_text.itertext())
                label = abstract_text.attrib.get("Label")

                if label:
                    abstract_parts.append(f"{label}: {text}")
                else:
                    abstract_parts.append(text)

            abstract = " ".join(abstract_parts)

            year = article.findtext(
                ".//PubDate/Year",
                default=""
            )

            journal = article.findtext(
                ".//Journal/Title",
                default=""
            )

            articles.append({
                "pmid": pmid,
                "title": title,
                "abstract": abstract,
                "year": year,
                "journal": journal,
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
            })

        return articles

    def retrieve(self, query):
        pmids = self.search_articles(query)
        articles = self.fetch_articles(pmids)

        # PMID 기준 중복 제거
        unique_articles = {}
        for article in articles:
            if article["pmid"]:
                unique_articles[article["pmid"]] = article

        return list(unique_articles.values())


if __name__ == "__main__":
    retriever = PubMedRetriever(max_results=5)

    query = "vaccination AND infectious diseases"

    articles = retriever.retrieve(query)

    print("\nPUBMED RETRIEVAL RESULTS")
    print("=" * 65)

    for index, article in enumerate(articles, start=1):
        print(f"\n{index}. {article['title']}")
        print("PMID:", article["pmid"])
        print("Year:", article["year"])
        print("Journal:", article["journal"])
        print("Abstract:", article["abstract"][:500])
        print("URL:", article["url"])