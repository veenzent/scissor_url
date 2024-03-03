from fastapi import FastAPI
from scissorapp.routers.link_shortener import url_shortener
from scissorapp import models
from scissorapp.database import Base, engine


app = FastAPI()
app.include_router(url_shortener)


models.Base.metadata.create_all(bind=engine)
existing_tables = Base.metadata.tables.keys()
print("Existing tables:", existing_tables)


@app.get("/")
def home():
    return {"msg": "Welcome to Scissor URL :)"}
