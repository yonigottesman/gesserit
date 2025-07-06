import importlib.resources as resources
from functools import partial
from typing import Callable

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory=resources.files(__package__) / "templates")


class Gesserit:
    def __init__(self, handler: Callable):
        self.app = FastAPI()
        self.handler = handler
        self.app.add_api_route(
            "/", partial(root, search_function=self.handler), response_class=HTMLResponse, methods=["GET"]
        )

    def run(self, **kwargs):
        uvicorn.run(self.app, **kwargs)


def root(request: Request, search_function: Callable) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request, "message": search_function()})
