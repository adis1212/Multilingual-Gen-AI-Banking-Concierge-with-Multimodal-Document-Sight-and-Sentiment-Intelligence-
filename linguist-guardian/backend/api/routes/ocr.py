from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from core.gpt4o_client import analyze_document
import base64

router = APIRouter()


@router.post("/analyze")
async def analyze_doc(
    image: UploadFile = File(...),
    doc_type: str = Form("aadhaar"),
    customer_record: str = Form("{}"),
):
    """Analyze document image with GPT-4o Vision."""
    import json

    if image.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(400, "Unsupported image format. Use JPEG/PNG/WEBP.")

    image_bytes = await image.read()
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    try:
        customer_data = json.loads(customer_record)
    except Exception:
        customer_data = {}

    result = await analyze_document(image_b64, doc_type, customer_data)
    return result