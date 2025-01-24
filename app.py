from fastapi import Request, FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# TODO: hide your API key as a space's SECRET, access it via environment variable

@app.post("/api/test")
async def api_test(request: Request):
  return {
    "message": "This is a test",
    "what_you_sent": await request.json(),
  }

app.mount("/", StaticFiles(directory="static", html=True), name="static")
