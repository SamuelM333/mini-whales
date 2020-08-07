from typing import List

import aiodocker
from aiodocker.containers import DockerContainer
from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"))

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    container_list_data = []
    async with aiodocker.Docker() as docker:
        container_list: List[DockerContainer] = await docker.containers.list()
        for container in container_list:
            container_metadata = await container.show()
            container_list_data.append({
                "name": container_metadata.get("Name")[1:],
                "id": container_metadata.get("Id")[:12],
                "image": container_metadata.get("Config").get("Image"),
            })
            context = {
                "request": request,
                "container_list": container_list_data,
            }
    return templates.TemplateResponse("index.html", context)


@app.get("/container/{container_id}/", response_class=HTMLResponse)
async def container_view(request: Request, container_id: str):
    async with aiodocker.Docker() as docker:
        container = await docker.containers.get(container_id)
        container_metadata = await container.show()
    context = {
        "request": request,
        "container_id": container_id,
        "container_name": container_metadata.get("Name")[1:],
    }
    return templates.TemplateResponse("container.html", context)


@app.websocket('/container/{container_id}/')
async def ws(websocket: WebSocket, container_id: str):
    await websocket.accept()
    async with aiodocker.Docker() as docker:
        container = await docker.containers.get(container_id)
        logs = container.log(stdout=True, stderr=True, follow=True, tail=50)
        async for line in logs:
            await websocket.send_text(line)