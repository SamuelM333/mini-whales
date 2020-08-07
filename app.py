from typing import List

import docker
import aiodocker
from docker.models.containers import Container
from aiodocker.containers import DockerContainer
from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"))

docker_client = docker.from_env()
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    container_list: List[Container] = docker_client.containers.list()
    context = {
        "request": request,
        "container_list": container_list,
    }
    return templates.TemplateResponse("index.html", context)


@app.get("/container/{container_id}/", response_class=HTMLResponse)
async def container_view(request: Request, container_id: str):
    container = docker_client.containers.get(container_id)
    context = {
        "request": request,
        "container": container
    }
    return templates.TemplateResponse("container.html", context)


@app.websocket('/container/{container_id}/')
async def ws(websocket: WebSocket, container_id: str):
    await websocket.accept()
    async with aiodocker.Docker() as docker:
        container: DockerContainer = await docker.containers.get(container_id)
        logs = container.log(stdout=True, stderr=True, follow=True, tail=50)
        async for line in logs:
            await websocket.send_text(line)
