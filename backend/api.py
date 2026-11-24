
import inspect
import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.evidence_pipeline import EvidencePipeline


API_VERSION = "2026-11-24.7"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("medical_factguard")


app = FastAPI(
    title="Medical FactGuard AI API",
    description="Medical evidence analysis API",
    version=API_VERSION,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


pipeline = None


class AnalysisRequest(BaseModel):
    claim: str = Field(
        ...,
        min_length=5,
        max_length=2000,
        description="Medical claim to analyze",
    )


def get_pipeline():
    global pipeline

    if pipeline is None:
        pipeline = EvidencePipeline()

        if not hasattr(pipeline, "claim_translator"):
            raise RuntimeError(
                "The loaded EvidencePipeline does not contain "
                "the ClaimTranslator. Check the imported file."
            )

        if not callable(
            getattr(pipeline.claim_translator, "translate_to_english", None)
        ):
            raise RuntimeError(
                "ClaimTranslator.translate_to_english is unavailable."
            )

        logger.info(
            "EvidencePipeline initialized from: %s",
            inspect.getfile(EvidencePipeline),
        )

    return pipeline


@app.get("/")
def root():
    return {
        "name": "Medical FactGuard AI",
        "status": "running",
        "version": API_VERSION,
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "Medical FactGuard AI API",
        "api_version": API_VERSION,
        "pipeline_module": inspect.getfile(EvidencePipeline),
        "translation_supported": hasattr(
            EvidencePipeline,
            "analyze_claim",
        ),
    }


@app.post("/analyze")
def analyze_claim(request: AnalysisRequest):

    claim = request.claim.strip()

    if not claim:
        raise HTTPException(
            status_code=400,
            detail="Claim cannot be empty.",
        )

    try:
        engine = get_pipeline()

        result = engine.analyze_claim(claim)

        if not isinstance(result, dict):
            raise RuntimeError(
                "EvidencePipeline returned an invalid response."
            )

        # Prevent an older pipeline from silently searching
        # Korean input without translation.
        translation = result.get("claim_translation")
        search_summary = result.get("search_summary", {})

        if not isinstance(translation, dict):
            raise RuntimeError(
                "Translation metadata is missing. "
                "The loaded EvidencePipeline may be outdated."
            )

        translated_text = translation.get("translated_text")

        if not isinstance(translated_text, str) or not translated_text.strip():
            raise RuntimeError(
                "The translated claim is empty."
            )

        if search_summary.get("query_language") != "en":
            raise RuntimeError(
                "PubMed search was not performed in English."
            )

        return {
            "success": True,
            "api_version": API_VERSION,
            "result": result,
        }

    except HTTPException:
        raise

    except Exception as error:
        logger.exception("Medical FactGuard analysis failed")

        raise HTTPException(
            status_code=500,
            detail={
                "message": "Medical evidence analysis failed.",
                "error_type": type(error).__name__,
                "error": str(error),
            },
        )
