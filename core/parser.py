from bs4 import BeautifulSoup
import json, dataclasses

@dataclasses.dataclass
class Content:
    jsonable: bool
    content: str

def try_json(content: str):
    soup = BeautifulSoup(content, 'html.parser')
    try:
        json.loads(soup.text)
        return Content(jsonable=True, content=soup.text)
    except json.JSONDecodeError:
        return Content(jsonable=False, content=soup.prettify())