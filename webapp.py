"""Backward-compatible development entry point for the FastAPI application."""

import dotenv
import uvicorn

dotenv.load_dotenv()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=7860, reload=True)
