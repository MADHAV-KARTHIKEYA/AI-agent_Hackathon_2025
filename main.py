from dotenv import load_dotenv 
load_dotenv
from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import logging
import os
from typing import Dict
from config import Config
from query_processor import query_processor
from indexer import indexer
from slack_integration import slack_integration

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Internal AI Assistant", description="AI-powered assistant for internal company queries")

# Create necessary directories
os.makedirs("static/css", exist_ok=True)
os.makedirs("templates", exist_ok=True)
os.makedirs("log", exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up templates
templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup"""
    try:
        # Validate configuration
        Config.validate_config()
        
        # Index documents
        logger.info("Indexing documents...")
        indexer.index_documents()
        
        # Validate API key
        if not query_processor.validate_api_key():
            logger.warning("LLM API key not configured. Please set LLM_API_KEY in your environment.")
        
        logger.info("Application startup completed successfully")
        
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main chat interface"""
    return templates.TemplateResponse("base.html", {"request": request})

@app.post("/chat")
async def chat_endpoint(query: str = Form(...)):
    """Handle chat queries from the web interface"""
    try:
        if not query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        logger.info(f"Processing chat query: {query[:100]}...")
        
        # Process the query using the AI assistant
        response = query_processor.process_query(query)
        
        return {
            "status": "success",
            "query": query,
            "response": response
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat query: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/index")
async def reindex_documents():
    """Manually trigger document re-indexing"""
    try:
        logger.info("Manual document re-indexing triggered")
        documents = indexer.index_documents()
        
        return {
            "status": "success",
            "message": f"Successfully indexed {len(documents)} documents",
            "documents": list(documents.keys())
        }
        
    except Exception as e:
        logger.error(f"Error during manual indexing: {str(e)}")
        raise HTTPException(status_code=500, detail="Error during document indexing")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Internal AI Assistant",
        "api_configured": query_processor.validate_api_key()
    }

@app.get("/docs-list")
async def list_documents():
    """List all indexed documents"""
    try:
        if not indexer.documents:
            indexer.index_documents()
        
        return {
            "status": "success",
            "documents": list(indexer.documents.keys()),
            "total_count": len(indexer.documents)
        }
        
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving document list")

@app.post("/slack/events")
async def slack_events(request: Request):
    """Handle Slack events and interactions"""
    try:
        return await slack_integration.handle_slack_events(request)
    except Exception as e:
        logger.error(f"Error handling Slack event: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing Slack event")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=Config.DEBUG
    )
