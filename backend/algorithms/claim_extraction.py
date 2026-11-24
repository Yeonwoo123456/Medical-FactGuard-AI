
import re


class MedicalClaimExtractor:
    """
    Extracts medical claim candidates from English and Korean text.

    This module identifies candidate statements for further analysis.
    It does not determine whether a statement is medically true.
    """

    def __init__(self):

        # --------------------------------------------------
        # 1. Medical keywords
        # --------------------------------------------------

        self.english_medical_keywords = [
            "vaccine", "vaccines", "vaccination", "immunization",
            "medicine", "medication", "drug", "drugs",
            "treatment", "treatments", "therapy", "therapies",
            "cancer", "tumor", "tumour", "disease", "diseases",
            "infection", "infections", "virus", "viruses",
            "bacteria", "bacterial", "symptom", "symptoms",
            "side effect", "side effects",
            "cure", "clinical trial",
            "antibiotic", "antibiotics", "health",
            "medical", "patient", "patients",
            "blood pressure", "heart disease",
            "immune system", "immunity",
            "nutrition", "food poisoning", "bloating",
            "digestive system", "respiratory"
        ]

        self.korean_medical_keywords = [
            "백신", "예방접종", "면역", "면역력",
            "약", "의약품", "약물", "복용", "섭취",
            "치료", "치료제", "항생제",
            "암", "종양", "질병", "질환",
            "감염", "바이러스", "세균", "박테리아",
            "증상", "부작용", "합병증",
            "혈압", "심장병", "심혈관",
            "건강", "의학", "의료", "환자",
            "식중독", "소화", "위장", "호흡기",
            "염증", "통증", "알레르기",
            "영양", "음식", "식품",
            "체온", "발열", "설사", "구토",
            "세균 번식", "세균 감염"
        ]

        # --------------------------------------------------
        # 2. Claim indicators
        # --------------------------------------------------

        self.english_claim_indicators = [
            "cause", "causes", "caused", "causing",
            "prevent", "prevents", "prevented",
            "cure", "cures", "cured",
            "increase", "increases", "decrease", "decreases",
            "reduce", "reduces", "improve", "improves",
            "lead to", "leads to", "result in", "results in",
            "effective", "ineffective",
            "safe", "unsafe", "harmful", "beneficial",
            "proven", "evidence", "study", "studies",
            "associated with", "linked to",
            "suggest", "suggests", "show", "shows",
            "indicate", "indicates",
            "risk", "risks", "develop", "develops",
            "transmit", "transmits", "effectiveness",
            "confirmed", "fails", "failed",
            "works", "not effective",
            "no evidence", "not proven",
            "cannot prevent",
            "recommend", "recommended",
            "should", "must", "avoid"
        ]

        self.korean_claim_indicators = [
            "유발", "발생", "예방", "치료",
            "증가", "감소", "감소시", "높인다",
            "낮춘다", "줄인다", "늘린다",
            "개선", "악화", "완화",
            "효과", "효능", "효과적",
            "비효과적", "무효",
            "안전", "위험", "유해",
            "부작용", "합병증",
            "원인", "관련", "연관",
            "때문", "초래", "이어진다",
            "전염", "전파", "감염",
            "도움", "도움이 된다",
            "증상을 완화", "증상을 악화",
            "위험이 있다", "위험이 높다",
            "가능성이 있다", "가능하다",
            "나타난다", "나타날 수",
            "권장", "추천", "주의",
            "피해야", "금물", "삼가야",
            "섭취해야", "복용해야",
            "해야 한다", "해서는 안 된다",
            "필요하다", "필수적",
            "확인됐다", "밝혀졌다",
            "연구에 따르면", "연구 결과",
            "입증", "증명", "보고됐다"
        ]

    # --------------------------------------------------
    # 3. Sentence splitting
    # --------------------------------------------------

    def split_sentences(self, text):

        if not isinstance(text, str) or not text.strip():
            return []

        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")

        # Convert common visual separators into line breaks.
        text = re.sub(
            r"[◆◇♦▪●■▶►]+",
            "\n",
            text
        )

        # Split after sentence-ending punctuation.
        text = re.sub(
            r"(?<=[.!?。！？])\s+",
            "\n",
            text
        )

        # Split at line breaks and semicolons.
        raw_sentences = re.split(
            r"[\n;；]+",
            text
        )

        sentences = []

        for sentence in raw_sentences:

            sentence = re.sub(
                r"\s+",
                " ",
                sentence
            ).strip()

            # Remove leading list markers.
            sentence = re.sub(
                r"^[\-–—•*]+\s*",
                "",
                sentence
            ).strip()

            if len(sentence) >= 12:
                sentences.append(sentence)

        return sentences

    # --------------------------------------------------
    # 4. Keyword matching
    # --------------------------------------------------

    @staticmethod
    def contains_english_keyword(sentence, keywords):

        sentence_lower = sentence.lower()

        for keyword in keywords:

            pattern = (
                r"(?<![a-zA-Z])"
                + re.escape(keyword.lower())
                + r"(?![a-zA-Z])"
            )

            if re.search(pattern, sentence_lower):
                return True

        return False

    @staticmethod
    def contains_korean_keyword(sentence, keywords):

        for keyword in keywords:

            if keyword in sentence:
                return True

        return False

    def has_medical_keyword(self, sentence):

        return (
            self.contains_english_keyword(
                sentence,
                self.english_medical_keywords
            )
            or
            self.contains_korean_keyword(
                sentence,
                self.korean_medical_keywords
            )
        )

    # --------------------------------------------------
    # 5. Claim indicator matching
    # --------------------------------------------------

    def has_claim_indicator(self, sentence):

        return (
            self.contains_english_keyword(
                sentence,
                self.english_claim_indicators
            )
            or
            self.contains_korean_keyword(
                sentence,
                self.korean_claim_indicators
            )
        )

    # --------------------------------------------------
    # 6. Medical claim detection
    # --------------------------------------------------

    def is_medical_claim(self, sentence):

        if not sentence:
            return False

        return (
            self.has_medical_keyword(sentence)
            and self.has_claim_indicator(sentence)
        )

    # --------------------------------------------------
    # 7. Claim extraction
    # --------------------------------------------------

    def extract_claims(self, text):

        sentences = self.split_sentences(text)

        claims = []
        seen = set()

        for sentence in sentences:

            if not self.is_medical_claim(sentence):
                continue

            normalized = re.sub(
                r"\s+",
                " ",
                sentence.lower()
            ).strip()

            if normalized not in seen:

                claims.append(sentence)
                seen.add(normalized)

        return claims


# --------------------------------------------------
# 8. Test
# --------------------------------------------------

if __name__ == "__main__":

    extractor = MedicalClaimExtractor()

    sample_text = """
    백신은 감염병을 예방하는 데 도움을 줄 수 있다.
    운동은 건강을 유지하는 데 중요하다.
    항생제는 세균 감염 치료에 효과적이다.
    특정 음식은 식중독을 유발할 수 있다.
    여름철에는 세균 번식으로 식중독 위험이 증가한다.
    충분한 수분 섭취는 정상적인 신체 기능 유지에 도움이 된다.

    Some people claim that vaccines cause serious diseases.
    Exercise is important for maintaining good health.
    Antibiotics are effective against bacterial infections.
    Some cancer treatments have significant side effects.
    """

    results = extractor.extract_claims(sample_text)

    print("=" * 60)
    print("MEDICAL CLAIM EXTRACTION")
    print("=" * 60)

    if results:

        for index, claim in enumerate(results, start=1):
            print(f"{index}. {claim}")

    else:
        print("No medical claims detected.")

    print("\nTotal claims:", len(results))
