from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scissorapp.routers.link_shortener import url_shortener


app = FastAPI(title="Scissor URL API")

origins = [
    "http://127.0.0.1:5500",
    "https://v-scissor.netlify.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    # allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(url_shortener)


@app.get("/")
def home():
    return {"msg": "Welcome to Scissor URL :)"}
