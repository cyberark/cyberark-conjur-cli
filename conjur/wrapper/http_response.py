# -*- coding: utf-8 -*-

"""
Http response
This class wraps the aiohttp.ClientResponse for easy access
"""
import json

from aiohttp import ClientResponse


class HttpResponse:
    """
    Class HttpResponse wraps the aiohttp response object for easy access.
    """

    @staticmethod
    async def from_client_response(client_response: ClientResponse) -> 'HttpResponse':
        """ Create HttpResponse wrapper from aiohttp.ClientReponse, and read the response body """
        text = await client_response.text('utf-8')
        content = await client_response.read()
        return HttpResponse(client_response, text, content)

    def __init__(self,
                 client_response: ClientResponse,
                 text: str,
                 content: bytes):
        self._client_response = client_response
        self._text = text
        self._content = content

    def raise_for_status(self):
        """ Raise an exception if returned status reports an error """
        self._client_response.raise_for_status()

    @property
    def status(self) -> int:
        """ Return the response body as utf-8 text """
        return self._client_response.status

    @property
    def text(self) -> str:
        """ Return the response body as utf-8 text """
        return self._text

    @property
    def content(self) -> bytes:
        """ Return the response body as bytes """
        return self._content

    @property
    def json(self) -> json:
        """ Return the response body as json object based on utf-8 text """
        return json.loads(self.text)

    def __repr__(self):
        return f"{{'status': {self.status}, 'content length': '{len(self.content)}'}}"
