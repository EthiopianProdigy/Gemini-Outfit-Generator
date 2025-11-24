# backend/server.py
import os

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles

from fashion_ai import generate_outfit_image

# Load .env (for GEMINI_API_KEY etc.)
load_dotenv()

app = FastAPI()

# Serve static images from the backend folder (Tops/ and Bottoms/)
STATIC_ROOT = os.path.dirname(__file__)

app.mount(
    "/images",
    StaticFiles(directory=STATIC_ROOT),
    name="images",
)

# 🔥 CORS CONFIG – allow localhost:3000 explicitly
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,        # required if you pass cookies (you do not)
    allow_methods=["*"],
    allow_headers=["*"],
)

# Folder where uploaded user images are saved
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Folder & path for a persistent "profile" person image
PROFILE_DIR = os.path.join(os.path.dirname(__file__), "profile")
os.makedirs(PROFILE_DIR, exist_ok=True)
PROFILE_IMAGE_PATH = os.path.join(PROFILE_DIR, "person.png")

@app.post("/api/upload-person-image")
async def upload_person_image(image: UploadFile = File(...)):
    """
    Upload & save a persistent 'person' image to be reused in outfit generation.
    """
    # Save as profile/person.png (overwrite previous)
    with open(PROFILE_IMAGE_PATH, "wb") as f:
        f.write(await image.read())

    return {"success": True, "message": "Profile image saved."}


@app.post("/api/generate-outfit")
async def generate_outfit(
    prompt: str = Form(...),
    image: UploadFile | None = File(None),   # 👈 make image optional
):
    """
    Accepts a prompt and OPTIONAL uploaded image.
    If no image is provided, uses the saved profile image.
    """
    person_image_path: str

    if image is not None:
        # Save uploaded image (per-request override)
        file_location = os.path.join(UPLOAD_DIR, image.filename)
        with open(file_location, "wb") as f:
            f.write(await image.read())
        person_image_path = file_location
    else:
        # Use the persistent profile image
        person_image_path = PROFILE_IMAGE_PATH

    # Call your AI logic
    result = generate_outfit_image(prompt, person_image_path=person_image_path)

    if not result.get("success"):
        return JSONResponse(status_code=500, content=result)

    return result


@app.get("/health")
def health():
    return {"status": "ok"}