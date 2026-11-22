
import requests
import time

from typing import Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class PubMedRetriever:
    """
    Retrieves medical research articles from PubMed.

    Features:
    - ESearch for article IDs
    - EFetch for article details
    - Retry handling
    - Request interval control
    - PMID deduplication
    """

    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

    def __init__(
        self,
        max_results: int = 10,
        email: Optional[str] = None,
        api_key: Optional[str] = None,
        min_request_interval: float = 0.34,
    ):
        self.max_results = max_results
        self.email = email
        self.api_key = api_key
        self.min_request_interval = min_request_interval
        self._last_request_at = 0.0

        self.session = requests.Session()

        retry_strategy = Retry(
            total=3,
            backoff_factor=0.6,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)

        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def _request(self, endpoint: str, params: dict):
        """
        Sends a request to PubMed with rate limiting.
        """

        elapsed = time.monotonic() - self._last_request_at

        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)

        params["tool"] = "MedicalFactGuard"

        if self.email:
            params["email"] = self.email

        if self.api_key:
            params["api_key"] = self.api_key

        url = self.BASE_URL + endpoint

        response = self.session.get(
            url,
            params=params,
            timeout=(10, 30),
        )

        self._last_request_at = time.monotonic()

        response.raise_for_status()

        return response

    def search_articles(self, query: str):
        """
        Searches PubMed and returns PMID values.
        """

        params = {
            "db": "pubmed",
            "term": query,
            "retmax": self.max_results,
            "retmode": "json",
            "sort": "relevance",
        }

        response = self._request("esearch.fcgi", params)

        data = response.json()

        return data.get("esearchresult", {}).get("idlist", [])

    def fetch_articles(self, pmids: list):
        """
        Fetches article metadata and abstracts.
        """

        if not pmids:
            return []

        articles = []

        chunk_size = 200

        for start in range(0, len(pmids), chunk_size):
            chunk = pmids[start:start + chunk_size]

            params = {
                "db": "pubmed",
                "id": ",".join(chunk),
                "rettype": "abstract",
                "retmode": "xml",
            }

            response = self._request("efetch.fcgi", params)

            from xml.etree import ElementTree as ET

            root = ET.fromstring(response.content)

            for article in root.findall(".//PubmedArticle"):

                pmid = article.findtext(
                    ".//PMID",
                    default=""
                )

                title = article.findtext(
                    ".//ArticleTitle",
                    default=""
                )

                abstract_parts = []

                for abstract_text in article.findall(
                    ".//Abstract/AbstractText"
                ):
                    text = "".join(abstract_text.itertext()).strip()

                    if text:
                        abstract_parts.append(text)

                abstract = " ".join(abstract_parts)

                year = (
                    article.findtext(
                        ".//PubDate/Year",
                        default=""
                    )
                )

                if not year:
                    medline_date = article.findtext(
                        ".//PubDate/MedlineDate",
                        default=""
                    )

                    year = medline_date[:4] if medline_date else ""

                journal = article.findtext(
                    ".//Journal/Title",
                    default=""
                )

                if pmid:
                    articles.append({
                        "pmid": pmid,
                        "title": title,
                        "abstract": abstract,
                        "year": year,
                        "journal": journal,
                        "url": (
                            "https://pubmed.ncbi.nlm.nih.gov/"
                            f"{pmid}/"
                        ),
                    })

        return articles

    def retrieve(self, query: str):
        """
        Searches and retrieves articles.
        """

        pmids = self.search_articles(query)

        articles = self.fetch_articles(pmids)

        unique_articles = []
        seen_pmids = set()

        for article in articles:
            pmid = article.get("pmid")

            if not pmid or pmid in seen_pmids:
                continue

            seen_pmids.add(pmid)
            unique_articles.append(article)

        return unique_articles

    def close(self):
        self.session.close()


if __name__ == "__main__":

    retriever = PubMedRetriever(max_results=5)

    try:
        results = retriever.retrieve(
            "artificial intelligence in healthcare"
        )

        print(f"Retrieved articles: {len(results)}")

        for article in results:
            print("\nTitle:", article["title"])
            print("PMID:", article["pmid"])
            print("Year:", article["year"])
            print("URL:", article["url"])

    finally:
        retriever.close()