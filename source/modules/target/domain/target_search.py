from modules.target.schemas import (
    TargetTextSearchSchema,
    TargetImageSearchSchema,
    ListTargetsImageResponse,
    TargetSendImageSchemaResponse,
    CreateScanSchema,
    TargetTextSchemaResponse,
)
from services.serpapi.serp_config import SerpAPIController
from services.dorkgen.dork_generator import build_combined_dork
from database.repository import BaseRepository
from database.models.db_models import ScanHistory
from database.session import get_session
from source.services.facecrawler.facecrawler_service import (
    get_facecrawler_service,
)
import os
from typing import List


class TargetSearchService:
    def text_search(
        self, request: TargetTextSearchSchema
    ) -> List[TargetTextSchemaResponse]:
        dork_query = build_combined_dork(
            target_name=request.name, categories=request.categories
        )

        serp_api = SerpAPIController(api_key=os.getenv("SERPAPI_KEY"))
        response, status_code = serp_api.search(
            query=dork_query,
            location=request.country.value,
            engine=request.search_engine.value,
        )

        if status_code != 200 or not response.json().get("organic_results"):
            return []

        with get_session() as session:
            scan_repo = BaseRepository[ScanHistory, CreateScanSchema, None](ScanHistory)
            scan_repo.create(
                session=session,
                obj_in=CreateScanSchema(
                    query=dork_query,
                    engine=request.search_engine.value,
                    search_type="person",
                    status="STARTED",
                    image_metadata={
                        "country": request.country.value,
                        "categories": request.categories,
                    },
                ),
            )

        results = [
            TargetTextSchemaResponse(
                title=item.get("title", ""),
                link=item.get("link", ""),
                snippet=item.get("snippet", ""),
                source=item.get("source", "SerpAPI"),
            )
            for item in response.json().get("organic_results", [])
        ]

        return results


class TargetImageService:
    def __init__(self):
        self.client = get_facecrawler_service()

    def send_image(self, target_image: str) -> TargetSendImageSchemaResponse:
        response = self.client.handler.send_image(target_image)

        if response.status_code != 200:
            return TargetSendImageSchemaResponse(
                status="error",
                message="Failed to send image.",
                data=[],
            )

        result = self.client.check_response(response.json())
        if str(result.get("message")).startswith("error"):
            return TargetSendImageSchemaResponse(
                status="error", message=result["message"]
            )

        return TargetSendImageSchemaResponse(
            status="success", message=result["message"], id_search=result["id_search"]
        )

    def check_image_search(
        self, request: TargetImageSearchSchema
    ) -> ListTargetsImageResponse:
        response = self.client.check_progress(request.id_search, demo=request.demo)

        if response.get("message").startswith("error"):
            return ListTargetsImageResponse(
                status="error", message=response.get("message"), data=[]
            )

        return ListTargetsImageResponse(
            status="success",
            message=response.get("message"),
            data=response.get("data", []),
            progress=response.get("progress", 0),
            total=len(response.get("data", [])),
        )
