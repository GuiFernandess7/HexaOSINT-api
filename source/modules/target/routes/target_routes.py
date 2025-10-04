from fastapi import APIRouter, UploadFile, File, Depends
from modules.target.controllers import (
    get_target_text_data,
    send_target_image,
    get_target_image_data,
)
from modules.target.schemas import (
    TargetTextSearchSchema,
    TargetImageSearchSchema,
    ListTargetsResponse,
    TargetSendImageSchemaResponse,
    ListTargetsImageResponse,
)
from auth.config import get_current_active_user
from database.models.db_models import User
import tempfile
import os

router = APIRouter(prefix="/target", tags=["targets"])


@router.post("/text-search", response_model=ListTargetsResponse)
def search_text_target(
    request: TargetTextSearchSchema,
    current_user: User = Depends(get_current_active_user)
):
    return get_target_text_data(request, current_user.user_id)


@router.post("/image-search/send", response_model=TargetSendImageSchemaResponse)
def search_image_target(
    image_file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False, dir=".") as tmp:
        tmp.write(image_file.file.read())
        tmp.flush()
        temp_path = tmp.name

    try:
        response = send_target_image(temp_path)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    return response


@router.post("/image-search/receive", response_model=ListTargetsImageResponse)
def get_image_target(
    request: TargetImageSearchSchema,
    current_user: User = Depends(get_current_active_user)
):
    return get_target_image_data(request, current_user.user_id)
