from modules.target.schemas import (
    TargetTextSearchSchema,
    ListTargetsResponse,
    TargetImageSearchSchema,
    ListTargetsImageResponse,
    TargetSendImageSchemaResponse,
)
from modules.target.domain.target_search import (
    TargetSearchService,
    TargetImageService,
)
from uuid import UUID


def get_target_text_data(request: TargetTextSearchSchema, user_id: UUID) -> ListTargetsResponse:
    service = TargetSearchService()
    results = service.text_search(request, user_id)
    return ListTargetsResponse(data=results, total=len(results))


def send_target_image(target_image: str, user_id: UUID) -> TargetSendImageSchemaResponse:
    service = TargetImageService()
    return service.send_image(target_image, user_id)


def get_target_image_data(request: TargetImageSearchSchema, user_id: UUID) -> ListTargetsImageResponse:
    service = TargetImageService()
    return service.check_image_search(request, user_id)
