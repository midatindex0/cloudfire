from playwright.async_api import BrowserContext, Cookie
from aiohttp import ClientSession

from typing import Dict, Optional, List

class Response:
    def __init__(self, content: str, cookies: Optional[List[Cookie]] = None) -> None:
        self.cookies = cookies
        self.content = content


async def get_browser(browser: BrowserContext, url: str) -> Response:
    page = await browser.new_page()
    await page.goto(url)
    await page.wait_for_selector("h2#cf-challenge-running", state="detached")
    await page.wait_for_load_state("domcontentloaded")
    cookies = await page.context.cookies(url)
    html = await page.content()
    await page.close()
    return Response(cookies=cookies, content=html)


async def get_aiohttp(
    session: ClientSession,
    url: str,
    cookies: Dict[str, str] = None,
    browser: Browser = None,
    user_agent: str = None,
) -> Response:
    headers = {"User-Agent": user_agent}
    if cookies:
        res = await session.get(url, cookies=cookies, headers=headers)
        if res.status == 503 or res.status == 403:
            if not browser:
                raise Exception("Browser not provided. Aborting")
            return await get_browser(browser=browser, url=url)
        return Response(content=await res.text())
    else:
        res = await session.get(url, headers = headers)
        if res.status == 503 or res.status == 403:
            if not browser:
                raise Exception("Browser not provided. Aborting")
            return await get_browser(browser=browser, url=url)
        return Response(content=await res.text())


async def get(
    session: ClientSession,
    url: str,
    cookies: Dict[str, str] = None,
    browser: Browser = None,
    user_agent: str = None,
) -> Response:

    return await get_aiohttp(session, url, cookies, browser, user_agent=user_agent)
