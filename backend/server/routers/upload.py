from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from server.models.user import User
from server.middleware.auth_middleware import get_current_user
from server.utils.minio_client import upload_file, validate_image_ext
from server.config import get_settings

router = APIRouter(prefix="/upload", tags=["文件上传"])


@router.post("")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    settings = get_settings()
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名为空")

    file_ext = validate_image_ext(file.filename)
    if file_ext is None:
        raise HTTPException(status_code=400, detail="仅支持 jpg/jpeg/png/webp 格式")

    contents = await file.read()
    if len(contents) > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"文件大小不能超过 {settings.MAX_FILE_SIZE_MB}MB")

    url = await upload_file(contents, file_ext, prefix="uploads")

    return {"url": url}
