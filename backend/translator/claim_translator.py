"""Reliable Korean-to-English translation for Medical FactGuard AI.

Translation is deliberately performed at the start of EvidencePipeline.analyze_claim.
This module:
- preserves common medical terms with a small bilingual terminology glossary;
- supports DeepL or Google Cloud Translation when API keys are configured;
- falls back to Google's public web endpoint when no paid API key is configured;
- validates the result and fails closed instead of sending untranslated Korean
  into English-oriented keyword extraction or PubMed search.

Environment variables (optional):
    DEEPL_API_KEY
    GOOGLE_TRANSLATE_API_KEY
"""

import os
import re
from typing import Dict, List, Tuple

import requests


class ClaimTranslationError(RuntimeError):
    """Raised when a Korean claim cannot be translated safely."""


class ClaimTranslator:
    GOOGLE_WEB_ENDPOINT = "https://translate.googleapis.com/translate_a/single"
    GOOGLE_CLOUD_ENDPOINT = "https://translation.googleapis.com/language/translate/v2"
    DEEPL_ENDPOINT = "https://api-free.deepl.com/v2/translate"
    PROVIDER = "Google Translate web endpoint"
    MAX_INPUT_LENGTH = 4000

    # Longest phrases are protected first. These mappings focus on terms whose
    # mistranslation can change the medical subject, endpoint, or claim polarity.
    MEDICAL_GLOSSARY: Tuple[Tuple[str, str], ...] = (
        # Polarity-sensitive phrases must be protected before shorter positive
        # stems. This prevents "증가시키지 않는다" from becoming "increase".
        ("위험을 증가시키지 않습니다", "does not increase the risk"),
        ("위험을 증가시키지 않는다", "does not increase the risk"),
        ("위험을 증가시키지 않", "does not increase the risk"),
        ("위험을 감소시키지 않습니다", "does not reduce the risk"),
        ("위험을 감소시키지 않는다", "does not reduce the risk"),
        ("위험을 감소시키지 않", "does not reduce the risk"),
        ("위험을 증가시키", "increase the risk"),
        ("위험을 증가시킨", "increase the risk"),
        ("위험을 감소시키", "reduce the risk"),
        ("위험을 감소시킨", "reduce the risk"),
        ("위험을 높인다", "increases the risk"),
        ("위험을 낮춘다", "reduces the risk"),
        ("위험을 높이지 않는다", "does not increase the risk"),
        ("위험을 낮추지 않는다", "does not reduce the risk"),
        ("예방하지 못한다", "does not prevent"),
        ("예방하지 않는다", "does not prevent"),
        ("예방하지 않", "does not prevent"),
        ("예방하지 못하", "does not prevent"),
        ("증가하지 않는다", "does not increase"),
        ("증가하지 않", "does not increase"),
        ("감소하지 않는다", "does not decrease"),
        ("감소하지 않", "does not decrease"),
        ("높이지 않는다", "does not increase"),
        ("낮추지 않는다", "does not lower"),
        ("유발하지 않는다", "does not cause"),
        ("유발하지 않", "does not cause"),
        ("원인이 되지 않는다", "is not a cause of"),
        ("원인이 아니다", "is not a cause of"),
        ("인과관계가 없다", "has no causal relationship"),
        ("인과관계가 없", "has no causal relationship"),
        ("연관성이 없다", "is not associated"),
        ("연관성이 없", "is not associated"),
        ("관련성이 없다", "is not associated"),
        ("관련성이 없", "is not associated"),
        ("차이가 없다", "there is no difference"),
        ("효과가 없다", "is not effective"),
        ("통계적으로 유의하지 않", "not statistically significant"),

        # Korean disease/intervention terms mapped to searchable English names.
        ("헬리코박터 파일로리균", "Helicobacter pylori"),
        ("헬리코박터 파일로리", "Helicobacter pylori"),
        ("헬리코박터균", "Helicobacter pylori"),
        ("파일로리균", "Helicobacter pylori"),
        ("위암", "gastric cancer"),
        ("대장암", "colorectal cancer"),
        ("폐암", "lung cancer"),
        ("유방암", "breast cancer"),
        ("전립선암", "prostate cancer"),
        ("간암", "liver cancer"),
        ("췌장암", "pancreatic cancer"),
        ("고혈압", "hypertension"),
        ("당뇨병", "diabetes mellitus"),
        ("제2형 당뇨병", "type 2 diabetes"),
        ("심혈관 질환", "cardiovascular disease"),
        ("심장 질환", "heart disease"),
        ("뇌졸중", "stroke"),
        ("심근경색", "myocardial infarction"),
        ("고지혈증", "dyslipidemia"),
        ("이상지질혈증", "dyslipidemia"),
        ("비만", "obesity"),
        ("골다공증", "osteoporosis"),
        ("치매", "dementia"),
        ("알츠하이머병", "Alzheimer disease"),
        ("우울증", "depression"),
        ("천식", "asthma"),
        ("폐렴", "pneumonia"),
        ("독감", "influenza"),
        ("코로나19", "COVID-19"),
        ("코로나", "COVID-19"),
        ("신장 질환", "kidney disease"),
        ("만성 신장 질환", "chronic kidney disease"),
        ("감기", "common cold"),

        ("무작위 대조 시험", "randomized controlled trial"),
        ("무작위 배정 대조 시험", "randomized controlled trial"),
        ("체계적 문헌고찰", "systematic review"),
        ("메타 분석", "meta-analysis"),
        ("메타분석", "meta-analysis"),
        ("임상 시험", "clinical trial"),
        ("임상시험", "clinical trial"),
        ("이중맹검", "double-blind"),
        ("위약 대조", "placebo-controlled"),
        ("유의미한 차이가 없", "no significant difference"),
        ("발병 위험", "risk of developing the disease"),
        ("감기 증상", "common cold symptoms"),
        ("감기에 걸릴 위험", "risk of catching a common cold"),
        ("감기에 걸리", "catching a common cold"),
        ("감기 예방", "prevention of the common cold"),
        ("지속 기간", "duration"),
        ("부작용", "adverse effects"),
        ("이상 반응", "adverse events"),
        ("혈중 중성지방", "blood triglyceride levels"),
        ("중성지방 수치", "triglyceride levels"),
        ("혈당 수치", "blood glucose levels"),
        ("혈압을 낮추", "lower blood pressure"),
        ("칼슘 흡수", "calcium absorption"),
        ("수면의 질", "sleep quality"),
        ("기억력", "memory"),
        ("유산소 운동", "aerobic exercise"),
        ("식이섬유", "dietary fiber"),
        ("항생제", "antibiotics"),
        ("바이러스 감염", "viral infection"),
        ("비타민 C", "vitamin C"),
        ("비타민씨", "vitamin C"),
        ("비타민 D", "vitamin D"),
        ("아연 보충제", "zinc supplements"),
        ("아연", "zinc"),
        ("오메가-3 지방산", "omega-3 fatty acids"),
        ("오메가 3 지방산", "omega-3 fatty acids"),
        ("오메가-3", "omega-3"),
        ("카페인", "caffeine"),
        ("보충제를 복용", "take supplements"),
        ("꾸준히 섭취", "take regularly"),
        ("정기적으로 섭취", "take regularly"),
        ("섭취하면", "if consumed"),
        ("도움이 될 수 있", "may help"),
        ("가능성을 낮출 수 있", "may reduce the likelihood"),
        ("효과가 있", "is effective"),
        ("효과가 없", "is not effective"),
        ("관련이 있", "is associated with"),
        ("관련이 없", "is not associated with"),
        ("연관이 없다", "is not associated with"),
        ("연관이 없", "is not associated with"),
        ("관련이 없다", "is not associated with"),
        ("인과관계가 있다", "has a causal relationship with"),
        ("예방할 수 있", "can prevent"),
        ("치료할 수 있", "can treat"),
        ("감소시킬 수 있", "may reduce"),
        ("증가시킬 수 있", "may increase"),
        ("낮출 수 있", "may lower"),
        ("높일 수 있", "may increase"),
        ("아니다", "is not"),
        ("않는다", "does not"),
        ("없다", "does not have"),
        ("있다", "has"),
    )

    def __init__(self, timeout: Tuple[int, int] = (5, 25), session=None):
        self.timeout = timeout
        self.session = session or requests.Session()
        self.session.headers.update({
            "User-Agent": "MedicalFactGuardAI/1.1",
            "Accept": "application/json,text/plain,*/*",
        })

    @staticmethod
    def contains_hangul(text: str) -> bool:
        return bool(re.search(r"[\uac00-\ud7a3]", text or ""))

    @classmethod
    def _protect_glossary(cls, text: str) -> Tuple[str, Dict[str, str]]:
        """Replace recognized Korean medical phrases with stable placeholders."""
        protected = {}
        output = text
        for index, (korean, english) in enumerate(
            sorted(cls.MEDICAL_GLOSSARY, key=lambda item: len(item[0]), reverse=True)
        ):
            if korean not in output:
                continue
            token = f"MGTERMZXQ{index:03d}QXZ"
            # Avoid accidental token collision with user-provided text.
            while token in output:
                token += "X"
            output = output.replace(korean, token)
            protected[token] = english
        return output, protected

    @staticmethod
    def _restore_glossary(text: str, protected: Dict[str, str]) -> str:
        output = text
        for token, english in protected.items():
            output = output.replace(token, english)
        return output

    def _translate_deepl(self, text: str, api_key: str) -> str:
        response = self.session.post(
            self.DEEPL_ENDPOINT,
            headers={"Authorization": f"DeepL-Auth-Key {api_key}"},
            data={"text": text, "source_lang": "KO", "target_lang": "EN-US"},
            timeout=self.timeout,
        )
        response.raise_for_status()
        data = response.json()
        translations = data.get("translations") or []
        if not translations or not translations[0].get("text"):
            raise ValueError("DeepL returned no translated text.")
        return translations[0]["text"].strip()

    def _translate_google_cloud(self, text: str, api_key: str) -> str:
        response = self.session.post(
            self.GOOGLE_CLOUD_ENDPOINT,
            params={"key": api_key},
            json={
                "q": text,
                "source": "ko",
                "target": "en",
                "format": "text",
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        data = response.json()
        translations = data.get("data", {}).get("translations", [])
        if not translations or not translations[0].get("translatedText"):
            raise ValueError("Google Cloud Translation returned no translated text.")
        return requests.utils.unquote(translations[0]["translatedText"]).strip()

    def _translate_google_web(self, text: str) -> str:
        response = self.session.get(
            self.GOOGLE_WEB_ENDPOINT,
            params={
                "client": "gtx",
                "sl": "ko",
                "tl": "en",
                "dt": "t",
                "q": text,
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        payload = response.json()
        translated = "".join(
            segment[0]
            for segment in (payload[0] or [])
            if isinstance(segment, list) and segment and segment[0]
        ).strip()
        if not translated:
            raise ValueError("Google translation returned empty text.")
        return translated

    def _translate(self, text: str) -> Tuple[str, str]:
        deepl_key = os.getenv("DEEPL_API_KEY", "").strip()
        google_key = os.getenv("GOOGLE_TRANSLATE_API_KEY", "").strip()

        errors: List[str] = []
        providers = []
        if deepl_key:
            providers.append(("DeepL API", lambda: self._translate_deepl(text, deepl_key)))
        if google_key:
            providers.append(("Google Cloud Translation API",
                              lambda: self._translate_google_cloud(text, google_key)))
        providers.append(("Google Translate web endpoint",
                          lambda: self._translate_google_web(text)))

        for provider_name, operation in providers:
            try:
                translated = operation()
                if translated:
                    return translated, provider_name
            except Exception as error:
                errors.append(f"{provider_name}: {type(error).__name__}: {error}")

        detail = "; ".join(errors[-3:])
        raise ClaimTranslationError(
            "Korean-to-English translation failed. No keyword extraction or PubMed "
            "search was performed. Check the translation service/network and retry. "
            + detail
        )

    def translate_to_english(self, claim: str) -> Dict[str, object]:
        if not isinstance(claim, str) or not claim.strip():
            raise ValueError("Claim must be a non-empty string.")

        original = claim.strip()
        if len(original) > self.MAX_INPUT_LENGTH:
            raise ValueError(
                f"Claim is too long. Maximum supported length is "
                f"{self.MAX_INPUT_LENGTH} characters."
            )

        if not self.contains_hangul(original):
            return {
                "source_language": "en",
                "translated_text": original,
                "translation_applied": False,
                "provider": "None (English input)",
                "glossary_terms_applied": [],
                "translation_validated": True,
            }

        protected_text, protected_terms = self._protect_glossary(original)
        translated_raw, provider = self._translate(protected_text)
        translated = self._restore_glossary(translated_raw, protected_terms)
        translated = re.sub(r"\s+", " ", translated).strip()

        if not translated:
            raise ClaimTranslationError("Translation returned an empty result.")
        if self.contains_hangul(translated):
            raise ClaimTranslationError(
                "Translation validation failed: Korean characters remain in the "
                "English translation. Search and analysis were stopped."
            )
        if len(translated) < max(4, int(len(original) * 0.12)):
            raise ClaimTranslationError(
                "Translation validation failed: the translated text is unexpectedly short."
            )

        return {
            "source_language": "ko",
            "translated_text": translated,
            "translation_applied": True,
            "provider": provider,
            "glossary_terms_applied": list(protected_terms.values()),
            "translation_validated": True,
        }