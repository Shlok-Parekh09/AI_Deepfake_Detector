from fastapi import FastAPI

app = FastAPI(title="AI Deepfake Detector API")

@app.get("/")
def read_root():
    return {"message": "Welcome to AI Deepfake Detector API"}
