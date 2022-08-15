from playwright.async_api import BrowserContext, Cookie
from aiohttp import ClientSession


from typing import Optional, List

from core.cookies import CookieManager


class Response:
    def __init__(
        self, content: str, status: int, cookies: Optional[List[Cookie]] = None
    ) -> None:
        self.status = status
        self.cookies = cookies
        self.content = content


class RequestManager:
    def __init__(
        self,
        session: ClientSession,
        browser: BrowserContext = None,
        cookie_manager: CookieManager = None,
        user_agent: str = None,
    ) -> None:
        self.session = session
        self.browser = browser
        self.cookie_manager = cookie_manager
        self.user_agent = user_agent

    async def _get_browser(self, url: str) -> Response:
        page = await self.browser.new_page()
        await page.goto(url)
        async with page.expect_response(url) as res_info:
            await page.wait_for_selector("h2#cf-challenge-running", state="detached")
            await page.wait_for_load_state("domcontentloaded")
        status = (await res_info.value).status
        cookies = await page.context.cookies(url)
        html = await page.content()
        await page.close()
        await self.cookie_manager.add_cookies(cookies)
        return Response(cookies=cookies, content=html, status=status)

    async def _get_aiohttp(
        self,
        url: str,
    ) -> Response:
        headers = {"User-Agent": self.user_agent}
        if await self.cookie_manager.get_cookies(url):
            res = await self.session.get(
                url, cookies=await self.cookie_manager.get_cookies(url), headers=headers
            )
            if res.status == 503 or res.status == 403:
                if not self.browser:
                    raise Exception("Browser not provided. Aborting")
                return await self._get_browser(url=url)
            return Response(content=await res.text(), status=res.status)
        else:
            res = await self.session.get(url, headers=headers)
            if res.status == 503 or res.status == 403:
                if not self.browser:
                    raise Exception("Browser not provided. Aborting")
                return await self._get_browser(url=url)
            return Response(content=await res.text(), status=res.status)

    async def get(self, url: str) -> Response:

        return await self._get_aiohttp(url)
