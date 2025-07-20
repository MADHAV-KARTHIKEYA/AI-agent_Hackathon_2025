import os
from dotenv import load_dotenv

load_dotenv()  # <- Load the .env file

from flask import Flask, request, jsonify
from slack_bolt import App
from flask import Flask, request, jsonify
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT
from whoosh.qparser import QueryParser
from google.oauth2 import service_account
from googleapiclient.discovery import build
import requests
from transformers import pipeline

# --- Setup --- #
app = Flask(__name__)

# Slack setup (replace with your tokens)
slack_app = App(
    token=os.getenv("SLACK_BOT_TOKEN"),
    signing_secret=os.getenv("SLACK_SIGNING_SECRET")
)
handler = SlackRequestHandler(slack_app)

# Whoosh search index
schema = Schema(title=TEXT(stored=True), content=TEXT(stored=True))
if not os.path.exists("indexdir"):
    os.mkdir("indexdir")
    ix = create_in("indexdir", schema)
else:
    ix = open_dir("indexdir")

# Google Docs API setup (optional)
SCOPES = ['https://www.googleapis.com/auth/documents.readonly']
SERVICE_ACCOUNT_FILE = 'service_account.json'
credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
docs_service = build('docs', 'v1', credentials=credentials)

# QA pipeline
qa_pipeline = pipeline("question-answering", model="deepset/roberta-base-squad2")

# --- Helper Functions --- #
def index_from_google_doc(doc_id):
    """Fetch and index a Google Doc by ID."""
    doc = docs_service.documents().get(documentId=doc_id).execute()
    content = ""
    for elem in doc['body']['content']:
        if 'paragraph' in elem:
            for text in elem['paragraph']['elements']:
                content += text.get('textRun', {}).get('content', '')
    writer = ix.writer()
    writer.add_document(title=f"GoogleDoc_{doc_id}", content=content)
    writer.commit()

def index_from_notion(page_id):
    """Index a Notion page (simplified). Requires Notion API."""
    # Placeholder: Use Notion's API to fetch page content
    pass

def search_docs(query):
    """Search indexed documents."""
    with ix.searcher() as searcher:
        query_parser = QueryParser("content", ix.schema)
        parsed_query = query_parser.parse(query)
        results = searcher.search(parsed_query, limit=3)
        return [{"title": hit['title'], "content": hit['content']} for hit in results]

# --- Slack Commands --- #
@slack_app.command("/ask")
def handle_ask(ack, respond, command):
    ack()
    query = command['text']
    results = search_docs(query)
    if not results:
        respond(text="No results found.")
        return
    
    # Get the most relevant answer
    answer = qa_pipeline(question=query, context=results[0]['content'])
    respond(text=f"*{results[0]['title']}*\n{answer['answer']}")

# --- Flask Routes --- #
@app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)

@app.route('/index-update', methods=['POST'])
def update_index():
    """Endpoint to manually trigger re-indexing."""
    # Add logic to sync from Notion/Google Docs/Confluence
    return jsonify({"status": "Index updated"})

if __name__ == '__main__':
    app.run(debug=True)
