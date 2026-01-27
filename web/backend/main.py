"""FastAPI application entry point."""
import sys
from pathlib import Path
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import chat, providers, config


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events."""
    # Startup
    print("\n" + "="*60)
    print("✅ Agent Chat API Started Successfully!")
    print("="*60)
    print("📍 API Documentation: http://localhost:8000/docs")
    print("🔗 Backend URL: http://localhost:8000")
    print("⚡ Frontend will connect to this backend")
    print("="*60 + "\n")
    yield
    # Shutdown
    print("\n" + "="*60)
    print("🛑 Agent Chat API Shutting Down...")
    print("="*60 + "\n")


app = FastAPI(
    title="Agent Chat API",
    description="Web-based agent chat interface API",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware (allow frontend access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite + CRA
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router)
app.include_router(providers.router)
app.include_router(config.router)





@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Agent Chat API",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting backend server...")
    uvicorn.run(app, host="127.0.0.1", port=8000)


