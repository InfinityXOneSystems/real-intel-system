from fastapi import FastAPI
import os
import time

app = FastAPI()

@app.get("/")
def root():
    return {
        "service": "InfinityX Agents",
        "status": "online",
        "time": time.time()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
