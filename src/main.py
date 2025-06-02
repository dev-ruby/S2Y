import os

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from src.routers import fetch_playlist

# Get the absolute path to the project root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR)  # Serve static files from the project root

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="src/templates")

# Mount the directory containing index.html as static files
# This allows accessing index.html directly at the root URL
app.mount("/static", StaticFiles(directory="src/static"), name="static")

app.include_router(fetch_playlist.router)


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Serves the index.html file from the project root directory.
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify the server is running.
    """
    return {"status": "ok", "message": "Server is running."}
