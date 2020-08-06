import asyncio
from typing import List

import aiodocker
from aiodocker.containers import DockerContainer
from quart import Quart, websocket, render_template

app = Quart(__name__)
app.config['SECRET_KEY'] = 'secret'


@app.route("/")
async def index():
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
        "container_list": container_list_data
    }
    return await render_template("index.html", **context)


@app.route("/container/<container_id>/")
async def container_view(container_id):
    async with aiodocker.Docker() as docker:
        container = await docker.containers.get(container_id)
        container_metadata = await container.show()
    context = {
        "container_id": container_id,
        "container_name": container_metadata.get("Name")[1:],
    }
    return await render_template("container.html", **context)


@app.websocket('/container/<container_id>/')
async def ws(container_id):
    async with aiodocker.Docker() as docker:
        container = await docker.containers.get(container_id)
        logs = container.log(stdout=True, stderr=True, follow=True, tail=50)
        async for line in logs:
            await websocket.send(line)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    app.run(loop=loop)
    loop.close()
