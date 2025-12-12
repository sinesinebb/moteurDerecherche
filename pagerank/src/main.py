from fastapi import FastAPI
from src.core.config import settings
from src.api.routes import router

app = FastAPI(
    title="PageRank Service", 
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.include_router(router)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "pagerank",
        "version": "1.0.0"
    }

# Alternative avec slash pour compatibilité
@app.get("/health/")
async def health_check_slash():
    return {
        "status": "healthy", 
        "service": "pagerank",
        "version": "1.0.0"
    }

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "PageRank Service is running",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.service_port)