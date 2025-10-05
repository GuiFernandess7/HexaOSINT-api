from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from modules.target.routes.target_routes import router as target_router
from auth.routes import router as auth_router, limiter
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
import dotenv

dotenv.load_dotenv()
app = FastAPI(
    title="HexaOSINT API",
    description="A modular OSINT API for text and image searches",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  
        "http://localhost:3000",  
        "http://127.0.0.1:5173",  
        "http://127.0.0.1:3000",  
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/health-check")
def health_check():
    return {"status": "ok"}

app.include_router(auth_router)
app.include_router(target_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
