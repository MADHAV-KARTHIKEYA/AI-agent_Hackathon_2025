import logging
from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler
from fastapi import Request
from config import Config
from query_processor import query_processor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SlackIntegration:
    def __init__(self):
        self.app = None
        self.handler = None
        self.enabled = False
        
        # Initialize Slack app if tokens are available
        if Config.SLACK_BOT_TOKEN and Config.SLACK_SIGNING_SECRET:
            try:
                self.app = App(
                    token=Config.SLACK_BOT_TOKEN,
                    signing_secret=Config.SLACK_SIGNING_SECRET
                )
                self.handler = SlackRequestHandler(self.app)
                self.enabled = True
                self._setup_event_handlers()
                logger.info("Slack integration initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Slack integration: {str(e)}")
                self.enabled = False
        else:
            logger.warning("Slack tokens not configured. Slack integration disabled.")
    
    def _setup_event_handlers(self):
        """Set up Slack event handlers"""
        
        @self.app.message(".*")
        def handle_message_events(message, say):
            """Handle direct messages to the bot"""
            try:
                user_query = message['text']
                user_id = message['user']
                
                logger.info(f"Received Slack message from {user_id}: {user_query[:50]}...")
                
                # Process the query
                response = query_processor.process_query(user_query)
                
                # Send response back to Slack
                say(response)
                
            except Exception as e:
                logger.error(f"Error handling Slack message: {str(e)}")
                say("I'm sorry, I encountered an error processing your request. Please try again or contact IT support.")
        
        @self.app.command("/ask")
        def handle_ask_command(ack, respond, command):
            """Handle /ask slash command"""
            try:
                ack()  # Acknowledge the command
                
                user_query = command['text']
                user_id = command['user_id']
                
                if not user_query.strip():
                    respond("Please provide a question after the /ask command. Example: `/ask What's our refund policy?`")
                    return
                
                logger.info(f"Received /ask command from {user_id}: {user_query[:50]}...")
                
                # Process the query
                response = query_processor.process_query(user_query)
                
                # Send response
                respond(f"**Question:** {user_query}\n\n**Answer:** {response}")
                
            except Exception as e:
                logger.error(f"Error handling /ask command: {str(e)}")
                respond("I'm sorry, I encountered an error processing your request. Please try again or contact IT support.")
        
        @self.app.command("/help")
        def handle_help_command(ack, respond):
            """Handle /help slash command"""
            try:
                ack()
                
                help_text = """
**Internal AI Assistant Help**

I can help you find information about company policies, processes, and procedures.

**How to use:**
• Send me a direct message with your question
• Use `/ask [your question]` in any channel
• Use `/help` to see this message

**Example questions:**
• "What's our refund policy?"
• "How do I request design assets?"
• "What's the vacation policy?"
• "How does the onboarding process work?"

**Need more help?**
Contact IT support at it-support@company.com
                """
                
                respond(help_text)
                
            except Exception as e:
                logger.error(f"Error handling /help command: {str(e)}")
                respond("Error displaying help information. Please contact IT support.")
    
    async def handle_slack_events(self, request: Request):
        """Handle incoming Slack events"""
        if not self.enabled:
            return {"error": "Slack integration not configured"}
        
        try:
            return await self.handler.handle(request)
        except Exception as e:
            logger.error(f"Error handling Slack event: {str(e)}")
            return {"error": "Internal server error"}

# Global Slack integration instance
slack_integration = SlackIntegration()

# Setup instructions for Slack integration
SLACK_SETUP_INSTRUCTIONS = """
SLACK INTEGRATION SETUP INSTRUCTIONS:

1. Create a Slack App:
   - Go to https://api.slack.com/apps
   - Click "Create New App" > "From scratch"
   - Name your app "Internal AI Assistant"
   - Select your workspace

2. Configure Bot Token Scopes:
   - Go to "OAuth & Permissions"
   - Add these Bot Token Scopes:
     * app_mentions:read
     * channels:history
     * chat:write
     * commands
     * im:history
     * im:read
     * im:write

3. Install App to Workspace:
   - Click "Install to Workspace"
   - Copy the "Bot User OAuth Token" (starts with xoxb-)
   - Set this as SLACK_BOT_TOKEN in your environment

4. Configure Slash Commands:
   - Go to "Slash Commands"
   - Create command "/ask" with Request URL: https://your-domain.com/slack/events
   - Create command "/help" with Request URL: https://your-domain.com/slack/events

5. Enable Event Subscriptions:
   - Go to "Event Subscriptions"
   - Enable Events
   - Set Request URL: https://your-domain.com/slack/events
   - Subscribe to these bot events:
     * app_mention
     * message.im

6. Get Signing Secret:
   - Go to "Basic Information"
   - Copy "Signing Secret"
   - Set this as SLACK_SIGNING_SECRET in your environment

7. Add to FastAPI main.py:
   ```python
   from slack_integration import slack_integration
   
   @app.post("/slack/events")
   async def slack_events(request: Request):
       return await slack_integration.handle_slack_events(request)
   ```

8. Update your .env.local file with the tokens and restart the application.
"""

if __name__ == "__main__":
    print(SLACK_SETUP_INSTRUCTIONS)
