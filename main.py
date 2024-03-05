from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scissorapp.routers.link_shortener import url_shortener
from scissorapp import models
from scissorapp.database import Base, engine


app = FastAPI()

origins = [
    "http://localhost:5500"
    "http://localhost:5501"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
app.include_router(url_shortener)


models.Base.metadata.create_all(bind=engine)
existing_tables = Base.metadata.tables.keys()
print("Existing tables:", existing_tables)


@app.get("/")
def home():
    return {"msg": "Welcome to Scissor URL :)"}
