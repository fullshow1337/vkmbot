import io

import aiohttp

from .exceptions import MusicNotFound, VkApiError


class vk_music_api:
    def __init__ (self, access_token: str, user_agent: str):
        """
        Vk music api wrapper

        :param access_token:
        :param user_agent:
        """
        self._access_token = access_token
        self._user_agent = user_agent
        self._main_url = 'https://api.vk.com/'

    async def _send_request (self, method: str, params: dict) -> dict:
        """
        Send request vk music api

        :param method:
        :param params:
        """
        params['v'] = '5.95'
        params['access_token'] = self._access_token
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    url=f'{self._main_url}method/{method}', params=params,
                    headers={'User-Agent': self._user_agent}
            ) as response:
                return await response.json()

    async def search_music (self, query: str, count: int = 10,
                            offset: int = 0, sort: int = 0) -> dict:
        """
        Search music

        :param query:
        :param count:
        :param offset:
        :param sort:

        Sort param
        1 — by duration
        2 — by popularity
        0 — by date added
        """
        params = {'q': query, 'count': count, 'offset': offset,
                  'sort': sort}
        response = await self._send_request(method='audio.search',
                                            params=params)
        if response['response']['count'] != 0:
            return response['response']
        elif response['response']['count'] == 0:
            raise MusicNotFound('Music not found')

    async def get_music (self, audio_id: str) -> dict:
        """
        Get music by id
        Audio file ID, in the following format: {owner_id}_{audio_id}.

        :param audio_id:
        """
        params = {'audios': audio_id}
        response = await self._send_request(method='audio.getById',
                                            params=params)
        if not response.get('response'):
            raise VkApiError(response['error']['error_msg'])
        return response['response'][0]

    async def get_music_file (self, data: dict) -> dict:
        """
        Get audio file

        :param data:
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(url=data['url']) as response:
                response_content = await response.content.read()
                audio = io.BytesIO(initial_bytes=response_content)
                audio.name = f"{data['artist']} - {data['title']}"
                await session.close()
                return {'artist': data['artist'], 'title': data['title'],
                        'audio': audio}