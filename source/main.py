from fastapi import FastAPI
from modules.target.routes.target_routes import router as target_router
from auth.routes import router as auth_router
import dotenv

dotenv.load_dotenv()
app = FastAPI(
    title="HexaOSINT API",
    description="A modular OSINT API for text and image searches",
    version="1.0.0"
)

app.include_router(auth_router)
app.include_router(target_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
