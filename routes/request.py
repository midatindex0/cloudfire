from urllib.parse import urlparse
import logging, datetime

from fastapi import APIRouter
from fastapi.requests import Request
from pydantic import BaseModel, HttpUrl

from core import request as crequest

router = APIRouter()
logger = logging.getLogger("internal")

class GetReq(BaseModel):
    url: HttpUrl

@router.post("/get")
async def get(req: Request, payload: GetReq):
    logger.info(f"$GET: \"{payload.url}\" at {datetime.datetime.now().strftime('%I:%M%p')}")
    base = urlparse(payload.url).netloc
    cookies = await req.state.cookie_manager.get_cookies(base)
    res = await crequest.get(req.state.httpsession, payload.url, browser=req.state.browser, cookies=cookies, user_agent=req.state.user_agent)
    if res.cookies:
        await req.state.cookie_manager.add_cookies(res.cookies)
    return res
