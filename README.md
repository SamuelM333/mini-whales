# Mini Whales

This small POC is using:
 - [FastAPI](https://fastapi.tiangolo.com/)
 - [aiodocker](https://github.com/aio-libs/aiodocker): asyncio-friendly Docker API for Python

## How to run

First, run some Docker containers either with Docker or Docker Compose.

To run the app:

```shell script
# inside a virtualenv
pip install -r requirements.txt  
uvicorn app:app --port 5000 --reload
```

Now check http://localhost:5000 and click in a container. To save some time scrolling, I limited the amount of lines
initially retrieved to 50, but this is easily configurable and not a requirement.

**Note: Python 3.6 or newer is required**
