import os
from fastapi import Request, FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# TODO: hide your API key as a space's SECRET, access it via environment variable
API_KEY = os.environ.get("API_KEY")

@app.post("/api/test")
async def api_test(request: Request):
  return {
    "message": "This is a test",
    "what_you_sent": await request.json(),
    "my_secret_api_key": API_KEY,
  }

app.mount("/", StaticFiles(directory="static", html=True), name="static")
