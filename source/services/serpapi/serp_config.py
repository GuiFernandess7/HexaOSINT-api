from enums.search_type import SearchEnum
import requests as rq
import os


class SerpAPIController:
    def __init__(
        self, api_key: str, search_type: SearchEnum = SearchEnum.GOOGLE_SEARCH
    ):
        self.api_key = api_key
        self.search_type = search_type

    def search(self, query: str, location: str = "Brazil", engine: str = "google"):
        response = rq.get(
            f"https://serpapi.com/{self.search_type.value}",
            params={
                "q": query,
                "location": location,
                "api_key": self.api_key,
                "engine": engine,
            },
        )
        return response, response.status_code
