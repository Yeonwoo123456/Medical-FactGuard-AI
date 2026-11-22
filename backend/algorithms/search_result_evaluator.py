
import re
import math

from collections import Counter
from typing import Dict, List, Any


class SearchResultEvaluator:
    """
    Evaluates how relevant PubMed articles are to a medical claim.

    Important:
    - Relevance does NOT mean truth.
    - A high score does NOT mean an article supports the claim.
    - This is a lexical matching method, not a semantic or clinical evaluation.
    """

    STOPWORDS = {
        "a", "an", "the", "is", "are", "was", "were",
        "be", "been", "being", "to", "of", "in", "on",
        "for", "with", "by", "from", "and", "or", "but",
        "that", "this", "these", "those", "it", "its",
        "as", "at", "into", "about", "than", "then",
        "can", "could", "may", "might", "should", "would",
        "does", "do", "did", "has", "have", "had",
        "not", "no", "such", "their", "they", "them",
        "we", "our", "us", "which", "who", "what",
        "when", "where", "while", "after", "before",
    }

    def __init__(self):
        pass

    def tokenize(self, text: str) -> List[str]:
        """
        Converts text into normalized tokens.
        """

        if not text:
            return []

        tokens = re.findall(
            r"[a-zA-Z0-9]+",
            text.lower()
        )

        return [
            token
            for token in tokens
            if token not in self.STOPWORDS
            and len(token) > 1
        ]

    def calculate_cosine_similarity(
        self,
        text_a: str,
        text_b: str
    ) -> float:
        """
        Calculates lexical cosine similarity.
        """

        tokens_a = self.tokenize(text_a)
        tokens_b = self.tokenize(text_b)

        if not tokens_a or not tokens_b:
            return 0.0

        vector_a = Counter(tokens_a)
        vector_b = Counter(tokens_b)

        common_tokens = set(vector_a) & set(vector_b)

        dot_product = sum(
            vector_a[token] * vector_b[token]
            for token in common_tokens
        )

        magnitude_a = math.sqrt(
            sum(value ** 2 for value in vector_a.values())
        )

        magnitude_b = math.sqrt(
            sum(value ** 2 for value in vector_b.values())
        )

        if magnitude_a == 0 or magnitude_b == 0:
            return 0.0

        return dot_product / (
            magnitude_a * magnitude_b
        )

    def evaluate_article(
        self,
        claim: str,
        article: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluates one article against a claim.

        Title relevance receives 40%.
        Abstract relevance receives 60%.
        """

        title = article.get("title", "")
        abstract = article.get("abstract", "")

        title_score = self.calculate_cosine_similarity(
            claim,
            title
        )

        abstract_score = self.calculate_cosine_similarity(
            claim,
            abstract
        )

        relevance_score = (
            0.4 * title_score
            + 0.6 * abstract_score
        )

        return {
            "pmid": article.get("pmid"),
            "title_score": round(title_score, 4),
            "abstract_score": round(abstract_score, 4),
            "relevance_score": round(relevance_score, 4),
        }

    def evaluate_articles(
        self,
        claim: str,
        articles: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Evaluates and ranks multiple articles.
        """

        evaluated = []

        for article in articles:

            result = self.evaluate_article(
                claim,
                article
            )

            evaluated.append({
                **article,
                "relevance": result,
            })

        evaluated.sort(
            key=lambda item: item["relevance"]["relevance_score"],
            reverse=True
        )

        return evaluated

    def calculate_query_score(
        self,
        claim: str,
        articles: List[Dict[str, Any]],
        top_k: int = 5
    ) -> float:
        """
        Calculates the overall quality of a search query
        based on the relevance of its retrieved articles.

        This is a retrieval relevance score, not a truth score.
        """

        if not articles:
            return 0.0

        evaluated = self.evaluate_articles(
            claim,
            articles
        )

        scores = [
            item["relevance"]["relevance_score"]
            for item in evaluated[:top_k]
        ]

        if not scores:
            return 0.0

        mean_score = sum(scores) / len(scores)

        claim_tokens = set(self.tokenize(claim))

        matched_tokens = set()

        for article in evaluated[:top_k]:

            text = (
                article.get("title", "")
                + " "
                + article.get("abstract", "")
            )

            matched_tokens.update(
                self.tokenize(text)
            )

        if not claim_tokens:
            coverage = 0.0
        else:
            coverage = (
                len(claim_tokens & matched_tokens)
                / len(claim_tokens)
            )

        final_score = (
            0.85 * mean_score
            + 0.15 * coverage
        )

        return round(final_score, 4)


if __name__ == "__main__":

    evaluator = SearchResultEvaluator()

    claim = (
        "Vaccines reduce the risk of severe infectious disease."
    )

    sample_articles = [
        {
            "pmid": "100001",
            "title": "Vaccine effectiveness against severe infectious diseases",
            "abstract": (
                "This study evaluates vaccine effectiveness "
                "in reducing severe disease outcomes."
            ),
        },
        {
            "pmid": "100002",
            "title": "A study about hospital management",
            "abstract": (
                "This research examines hospital administration "
                "and healthcare management."
            ),
        },
    ]

    results = evaluator.evaluate_articles(
        claim,
        sample_articles
    )

    for article in results:
        print("\nTitle:", article["title"])
        print(
            "Relevance:",
            article["relevance"]["relevance_score"]
        )

    query_score = evaluator.calculate_query_score(
        claim,
        sample_articles
    )

    print("\nOverall query score:", query_score)