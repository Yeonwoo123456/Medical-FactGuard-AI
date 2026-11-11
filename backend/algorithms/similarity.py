
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from sentence_transformers import SentenceTransformer


class SemanticSimilarity:

    def __init__(self, model_name="all-MiniLM-L6-v2"):

        # TF-IDF model
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2)
        )

        # Sentence Transformer model
        self.model = SentenceTransformer(model_name)

    # TF-IDF similarity
    def calculate_tfidf_similarity(self, claim, evidence):

        if not claim.strip() or not evidence.strip():
            return 0.0

        vectors = self.vectorizer.fit_transform([
            claim,
            evidence
        ])

        score = cosine_similarity(
            vectors[0:1],
            vectors[1:2]
        )[0][0]

        return float(score)

    # Sentence Transformer similarity
    def calculate_semantic_similarity(self, claim, evidence):

        if not claim.strip() or not evidence.strip():
            return 0.0

        embeddings = self.model.encode(
            [claim, evidence],
            normalize_embeddings=True
        )

        score = embeddings[0] @ embeddings[1]

        return float(score)

    # Compare multiple evidence documents
    def compare_multiple(self, claim, evidences):

        if not claim.strip():
            return []

        if not evidences:
            return []

        valid_evidences = [
            evidence for evidence in evidences
            if evidence.strip()
        ]

        if not valid_evidences:
            return []

        texts = [claim] + valid_evidences

        # Semantic embeddings
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True
        )

        semantic_scores = embeddings[1:] @ embeddings[0]

        # TF-IDF embeddings
        tfidf_vectors = self.vectorizer.fit_transform(texts)

        tfidf_scores = cosine_similarity(
            tfidf_vectors[0:1],
            tfidf_vectors[1:]
        )[0]

        results = []

        for evidence, semantic_score, tfidf_score in zip(
            valid_evidences,
            semantic_scores,
            tfidf_scores
        ):

            results.append({
                "evidence": evidence,
                "semantic_similarity": float(semantic_score),
                "tfidf_similarity": float(tfidf_score)
            })

        results.sort(
            key=lambda item: item["semantic_similarity"],
            reverse=True
        )

        return results


if __name__ == "__main__":

    similarity = SemanticSimilarity()

    claim = (
        "Vaccines can reduce the risk of "
        "infectious diseases."
    )

    evidences = [

        "Vaccination may lower the likelihood "
        "of contracting certain diseases.",

        "Vaccines are designed to stimulate "
        "the immune system.",

        "The weather is sunny today.",

        "Some medications can cause side effects."
    ]

    results = similarity.compare_multiple(
        claim,
        evidences
    )

    print("\nSEMANTIC SIMILARITY RESULTS")
    print("=" * 65)

    for index, result in enumerate(results, start=1):

        print(f"\n{index}. Evidence:")
        print(result["evidence"])

        print(
            "Semantic Similarity:",
            f"{result['semantic_similarity']:.4f}"
        )

        print(
            "TF-IDF Similarity:",
            f"{result['tfidf_similarity']:.4f}"
        )