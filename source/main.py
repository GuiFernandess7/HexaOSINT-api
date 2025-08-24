from fastapi import FastAPI
from modules.target.routes.target_routes import router as target_router
import dotenv

dotenv.load_dotenv()
app = FastAPI()
app.include_router(target_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
