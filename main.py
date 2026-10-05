from fastapi import FastAPI

app = FastAPI(title="TaskPilot AI",
              description="AI Powered personal Task tracker and remainder",
              version="1.0.0")

@app.get("/")
def health_check():
    return {
        "status": "Running",
        "message": "TaskPilot AI is running"
    }