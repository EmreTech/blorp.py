# MIT License
#
# Copyright (c) 2022 EmreTech
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import typing as t
from urllib.parse import quote

import aiohttp

__all__ = ("Route", "Client")


class Route:
    def __init__(self, method: str, url: str, **parameters: t.Any):
        self.method: str = method
        self.url: str = url.format_map({k: quote(str(v)) for k, v in parameters.items()})


class Client:
    def __init__(self, user_id: int, token: str):
        self.token: str = str(user_id) + "." + token
        self.default_headers: dict[str, str] = {"Authentication": self.token}
        self.__session: t.Optional[aiohttp.ClientSession] = None

    @property
    def _session(self):
        if (self.__session is not None and self.__session.closed) or self.__session is None:
            self.__session = aiohttp.ClientSession(headers=self.default_headers)

        return self.__session

    async def request(
        self, 
        route: Route, 
        *, 
        params: t.Optional[dict[str, str]] = None
    ) -> t.Optional[t.Any]:
        response = await self._session.request(route.method, route.url, params=params)

        if 200 <= response.status < 300:
            return await response.json()

        # TODO: raise http exception

    async def get_current_user(self):
        return self.request(Route("GET", "/user/@me"))

    async def get_all_users(self):
        return self.request(Route("GET", "/user/all"))

    async def get_user(self, user_id: int):
        return self.request(Route("GET", "/user/{user_id}", user_id=user_id))

    async def move(self, direction: t.Literal["UP", "DOWN", "RIGHT", "LEFT"]):
        return self.request(Route("POST", "/board/move/{direction}", direction=direction))

    async def dig(self):
        return self.request(Route("POST", "/board/dig"))

    async def attack(self, user_id: int):
        return self.request(Route("POST", "/user/{user_id}/attack", user_id=user_id))

    async def gift(self, user_id: int):
        return self.request(Route("POST", "/user/{user_id}/gift", user_id=user_id))
    
    async def get_board(self):
        return self.request(Route("GET", "/board"))
