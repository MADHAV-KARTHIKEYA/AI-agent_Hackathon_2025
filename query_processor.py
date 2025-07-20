import requests
import json
import logging
import os
from typing import Dict, Any
from config import Config
from indexer import indexer

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QueryProcessor:
    def __init__(self):
        self.api_key = Config.LLM_API_KEY
        self.endpoint = Config.LLM_ENDPOINT
        self.model = Config.LLM_MODEL
    
    def process_query(self, user_query: str) -> str:
        """Process a user query and return an AI-generated response"""
        try:
            # Get relevant context from indexed documents
            context = indexer.search_documents(user_query)
            
            # Prepare the system prompt
            system_prompt = """You are an internal AI assistant for a company. Your role is to help employees find information about internal processes, policies, and procedures.

You have access to the company's internal documentation. Use this information to provide accurate, helpful responses to employee questions.

Guidelines:
- Be concise but comprehensive
- Provide step-by-step instructions when applicable
- Include relevant contact information when available
- If you don't have specific information, suggest who to contact
- Be professional and helpful in tone

Context from company documents:
{context}
""".format(context=context)

            # Prepare the API request
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': self.model,
                'messages': [
                    {
                        'role': 'system',
                        'content': system_prompt
                    },
                    {
                        'role': 'user',
                        'content': user_query
                    }
                ],
                'temperature': 0.7,
                'max_tokens': 1000
            }
            
            # Make the API request
            response = requests.post(
                self.endpoint,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                response_data = response.json()
                ai_response = response_data['choices'][0]['message']['content']
                logger.info(f"Successfully processed query: {user_query[:50]}...")
                return ai_response
            else:
                logger.error(f"API request failed with status {response.status_code}: {response.text}")
                return "I'm sorry, I'm having trouble processing your request right now. Please try again later or contact IT support."
                
        except requests.exceptions.Timeout:
            logger.error("API request timed out")
            return "The request is taking longer than expected. Please try again."
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error: {str(e)}")
            return "I'm experiencing connectivity issues. Please check your network connection and try again."
        
        except KeyError as e:
            logger.error(f"Unexpected API response format: {str(e)}")
            return "I received an unexpected response. Please try rephrasing your question."
        
        except Exception as e:
            logger.error(f"Unexpected error processing query: {str(e)}")
            return "An unexpected error occurred. Please contact IT support if this continues."
    
    @staticmethod
    def validate_api_key() -> bool:
        """Validate that the API key is configured"""
        return bool(os.getenv("LLM_API_KEY"))

# Global query processor instance
query_processor = QueryProcessor()
