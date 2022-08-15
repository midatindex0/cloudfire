import logging, datetime

from fastapi import FastAPI, Request
from playwright.async_api import async_playwright
from aiohttp import ClientSession

from core import cookies
from core.request import RequestManager
from routes import request

app = FastAPI()
logger = logging.getLogger("internal")
handler = logging.FileHandler("logs.txt")
logger.addHandler(handler)
logger.setLevel(logging.INFO)


@app.on_event("startup")
async def config():
    logger.info("\n------New session starts here-------\n")
    logger.info(f"$DATE: {datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S%z')}\n")
    app.state.pwsession = await async_playwright().start()
    app.state.user_agent = (
        "Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0"
    )
    app.state.browser = await (
        await app.state.pwsession.firefox.launch(headless=True)
    ).new_context(user_agent=app.state.user_agent)
    app.state.httpsession = ClientSession()
    app.state.cookie_manager = cookies.CookieManager()
    app.state.request = RequestManager(
        session=app.state.httpsession,
        browser=app.state.browser,
        cookie_manager=app.state.cookie_manager,
        user_agent=app.state.user_agent,
    )


@app.middleware("http")
async def req_config(request: Request, call_next):
    request.state.browser = app.state.browser
    request.state.httpsession = app.state.httpsession
    request.state.cookie_manager = app.state.cookie_manager
    request.state.user_agent = app.state.user_agent
    request.state.request = app.state.request
    response = await call_next(request)
    return response


@app.on_event("shutdown")
async def shutdown():
    logger.info("\n-------Session ends here--------\n")
    await app.state.browser.close()
    await app.state.pwsession.stop()
    await app.state.httpsession.close()


app.include_router(request.router, tags=["request"])
