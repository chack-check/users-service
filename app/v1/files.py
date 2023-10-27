from urllib.parse import urljoin, urlencode

import aiohttp

from .schemas import FileUrl


class FilesSender:

    def __init__(self, service_url: str, headers: dict[str, str]):
        self._service_url = service_url
        self._session = aiohttp.ClientSession(headers=headers)

    @property
    def publish_url(self) -> str:
        return urljoin(self._service_url, "publish")

    def _construct_avatar_url(self, url: str) -> str:
        return url + '?response-content-type=image%2Fsvg%2Bxml'

    async def post_file(self, files: list[bytes]) -> list[FileUrl]:
        async with self._session as session:
            form_data = aiohttp.FormData()
            for file in files:
                form_data.add_field('files', file, filename="avatar.svg")

            async with session.post(self.publish_url, data=form_data) as response:
                if not response.ok:
                    print(await response.json())
                    return []

                response_json = await response.json()
                return [
                    FileUrl(filename=file['filename'], url=self._construct_avatar_url(file['url'])) for file in response_json
                ]

