from fastapi import FastAPI

app = FastAPI(title="FastAPI Application")


@app.get("/")
def home():
    return {"message": "FastAPI application is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}