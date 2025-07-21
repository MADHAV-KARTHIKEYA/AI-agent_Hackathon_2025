import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # LLM API Configuration
    LLM_API_KEY = os.getenv('LLM_API_KEY', '')
    LLM_ENDPOINT = 'https://openrouter.ai/api/v1/chat/completions'
    LLM_MODEL = 'openai/gpt-4o'
    
    # Slack Configuration
    SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN', '')
    SLACK_SIGNING_SECRET = os.getenv('SLACK_SIGNING_SECRET', '')
    
    # Application Configuration
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 8000))
    
    # Document Configuration
    DOCS_FOLDER = 'docs'
    LOG_FILE = 'log/app.log'
    
    @classmethod
    def validate_config(cls):
        """Validate critical configuration values"""
        if not cls.LLM_API_KEY:
            raise ValueError("LLM_API_KEY is required. Please set it in your environment variables.")
        
        if not cls.SLACK_BOT_TOKEN:
            print("Warning: SLACK_BOT_TOKEN not set. Slack integration will be disabled.")
        
        if not cls.SLACK_SIGNING_SECRET:
            print("Warning: SLACK_SIGNING_SECRET not set. Slack integration will be disabled.")
