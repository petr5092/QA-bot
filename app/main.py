from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from chat.router import router as chat_router

app = FastAPI()

# Serve static assets under /static to avoid intercepting API routes
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/files", StaticFiles(directory="files"), name="files")

@app.get("/")
def root():
	return FileResponse("static/index.html")

app.include_router(chat_router)
