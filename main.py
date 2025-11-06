from fastapi import FastAPI,

app = FastAPI()


@app.post("/text")
def read_root():
    return {"Hello": "World"}


