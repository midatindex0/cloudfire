import logging, datetime

from fastapi import APIRouter
from fastapi.requests import Request
from pydantic import BaseModel, HttpUrl

from core import parser

router = APIRouter()
logger = logging.getLogger("internal")


class GetReq(BaseModel):
    url: HttpUrl


@router.post("/get")
async def get(req: Request, payload: GetReq):
    logger.info(
        f"$GET: \"{payload.url}\" at {datetime.datetime.now().strftime('%I:%M%p')}"
    )
    res = await req.state.request.get(payload.url)
    data = parser.try_json(res.content)
    if data.jsonable:
        res.content = data.content
    return res
