import os
import re
import json
from typing import List, Dict
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from transformers import pipeline

# Dummy document loader (replace with actual APIs for Notion, Google Docs, Confluence)
def load_documents() -> List[Dict]:
    # Example: Replace with actual document fetching logic
    docs = [
        {"title": "Refund Policy", "content": "Our refund policy allows customers to request refunds within 30 days."},
        {"title": "Design Asset Request", "content": "To request design assets, fill out the form on our intranet."},
    ]
    return docs

# Simple document indexer
class DocumentIndexer:
    def __init__(self, documents: List[Dict]):
        self.documents = documents
        self.qa_pipeline = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")

    def search(self, question: str) -> str:
        best_answer = ""
        best_score = 0
        for doc in self.documents:
            result = self.qa_pipeline(question=question, context=doc["content"])
            if result['score'] > best_score:
                best_score = result['score']
                best_answer = result['answer']
        return best_answer if best_answer else "Sorry, I couldn't find an answer."

# Slack bot integration
class SlackBot:
    def __init__(self, token: str, indexer: DocumentIndexer):
        self.client = WebClient(token=token)
        self.indexer = indexer

    def handle_message(self, event_data):
        text = event_data.get('text', '')
        channel = event_data.get('channel')
        if text and channel:
            answer = self.indexer.search(text)
            try:
                self.client.chat_postMessage(channel=channel, text=answer)
            except SlackApiError as e:
                print(f"Slack error: {e.response['error']}")

# Main entry point
if __name__ == "__main__":
    # Load and index documents
    documents = load_documents()
    indexer = DocumentIndexer(documents)

    # Slack bot token (set as environment variable)
    SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
    if not SLACK_BOT_TOKEN:
        print("Please set the SLACK_BOT_TOKEN environment variable.")
        exit(1)

    slack_bot = SlackBot(SLACK_BOT_TOKEN, indexer)

    # Example: Simulate receiving a Slack message
    example_event = {
        "text": "What’s our refund policy?",
        "channel": "C1234567890"
    }
    slack_bot.handle_message(example_event)