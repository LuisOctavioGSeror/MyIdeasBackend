from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.controllers.auth import token_required
from app.infrastructure.storage.image_storage import get_image_storage

router = APIRouter(prefix="/uploads", tags=["Uploads"])


@router.post("/images")
async def upload_image(
    file: UploadFile = File(...),
    _auth=Depends(token_required),
):
    """
    Recebe uma imagem, envia para o storage configurado (S3/R2/etc.)
    e retorna a URL pública.
    """
    storage = get_image_storage()
    url = await storage.upload_image(file)
    if not url:
        raise HTTPException(status_code=500, detail="Failed to upload image.")
    return {"url": url}

