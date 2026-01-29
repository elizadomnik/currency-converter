from fastapi import FastAPI

app = FastAPI(title="Currency Converter API")

@app.get("/")
def read_root():
    return {"message": "Currency Converter API is running"}
