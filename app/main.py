from fastapi import FastAPI
from chat.router import router as chat_router

app = FastAPI()


app.include_router(chat_router)
