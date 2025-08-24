from modules.target.schemas import (
    TargetTextSearchSchema,
    ListTargetsResponse,
    TargetImageSearchSchema,
    TargetImageSchemaResponse,
    ListTargetsImageResponse,
    TargetSendImageSchemaResponse,
)
from services.facecheck.facecheck_service import (
    get_facecrawler_service,
)
from modules.target.domain.target_search import (
    TargetSearchService,
    TargetImageService,
)


def get_target_text_data(request: TargetTextSearchSchema) -> ListTargetsResponse:
    service = TargetSearchService()
    results = service.text_search(request)
    return ListTargetsResponse(data=results, total=len(results))


def send_target_image(target_image: str) -> TargetSendImageSchemaResponse:
    service = TargetImageService()
    return service.send_image(target_image)


def get_target_image_data(request: TargetImageSearchSchema) -> ListTargetsImageResponse:
    service = TargetImageService()
    return service.check_image_search(request)
