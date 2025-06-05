from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from src.routers import fetch_playlist
from src.configs import Config

app = FastAPI()


def convert_to_unix_line_endings(file_path):
    with open(file_path, "rb") as f:
        content = f.read()

    # Replace Windows line endings (\r\n) with Unix (\n)
    content = content.replace(b"\r\n", b"\n")

    with open(file_path, "wb") as f:
        f.write(content)


convert_to_unix_line_endings(Config.path.DOWNLOADER_SCRIPT)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory=Config.path.TEMPLATES_DIR)

app.mount("/static", StaticFiles(directory=Config.path.STATIC_DIR), name="static")

app.include_router(fetch_playlist.router)


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Server is running."}
