import time
import requests
import urllib.request
from typing import Optional, Dict, Tuple
import os
import dotenv
import json

dotenv.load_dotenv()


class FaceCrawlerHandler:
    """Handles the communication with the FaceCrawler API."""

    def __init__(self, api_key: str, site: str):
        self.api_key = api_key
        self.site = site
        self.headers = {
            "accept": "application/json",
            "Authorization": self.api_key,
        }

    def send_image(self, image_filepath: str) -> requests.Response:
        with open(image_filepath, "rb") as img_file:
            files = {"images": img_file, "id_search": None}
            response = requests.post(
                f"{self.site}/api/upload_pic", headers=self.headers, files=files
            )
        return response

    def search(
        self, id_search: str, with_progress=True, status_only=False, demo=False
    ) -> dict:
        payload = {
            "id_search": id_search,
            "with_progress": with_progress,
            "status_only": status_only,
            "demo": demo,
        }
        response = requests.post(
            f"{self.site}/api/search", headers=self.headers, json=payload
        )
        return response.json()


class FaceCrawlerService:
    """Service for handling face search operations using FaceCrawler API."""

    def __init__(self, handler: FaceCrawlerHandler):
        self.handler = handler

    def check_response(self, response: dict) -> dict:
        if response.get("error"):
            return {
                "message": f"error: {response.get('error')}",
                "status": response.get("code"),
                "id_search": None,
            }
        return {
            "message": "success",
            "status": response.get("code"),
            "id_search": response.get("id_search"),
        }

    def check_progress(
        self, id_search: str, demo=False
    ) -> Tuple[Optional[str], Optional[list]]:
        response = self.handler.search(id_search, demo=demo)
        if response.get("error"):
            return {
                "message": f"error: {response.get('error')}",
                "status": response.get("code"),
                "data": [],
            }

        if response.get("output"):
            for item in response["output"]["items"]:
                if "base64" in item:
                    item["base64"] = "[REMOVIDO PARA LOG]"

            return {
                "message": "search complete.",
                "status": response.get("code"),
                "progress": 100,
                "data": response["output"]["items"],
            }
        else:
            return {
                "message": "running search...",
                "status": response.get("code"),
                "progress": response.get("progress"),
                "data": [],
            }


def get_facecrawler_service() -> FaceCrawlerService:
    handler = FaceCrawlerHandler(
        api_key=os.getenv("FACECRAWLER_KEY"), site=os.getenv("SITE_URL")
    )
    service = FaceCrawlerService(handler=handler)
    return service
