Django Documentation Bot for Slack
This project is a Slack bot built with Django that assists users in finding relevant information from the Django documentation. Using a Retrieval-Augmented Generation (RAG) system, the bot can quickly locate, retrieve, and generate concise, helpful responses based on the official Django documentation. It is an efficient, automated assistant to help developers interact with Django documentation through Slack.

Table of Contents
. Overview
. Features
. Architecture
. Getting Started
. Environment Variables
. Usage
. Future Enhancements
. Contributing


Overview
The Django Documentation Bot aims to make it easy to access Django documentation directly within Slack, reducing the time spent browsing through the documentation manually. This bot uses a RAG (Retrieval-Augmented Generation) system that retrieves and generates responses based on queries, making it highly accurate and efficient.

Features
Instant Retrieval: Quickly finds and retrieves relevant sections of Django documentation.
RAG System: Combines retrieval and generation to provide contextually relevant answers.
Efficient Chunking: Uses a hierarchical chunking approach to manage documentation sections effectively.
Slack Integration: Deployable as a Slack bot, making documentation queries easy and interactive.
Embeddings: Uses sentence-transformers/all-MiniLM-L6-v2 for embedding generation to ensure efficient processing with minimal resource usage.
Architecture
The bot's RAG system is implemented with the following components:

Document Chunking: The Django documentation PDF is preprocessed and chunked into sections based on its hierarchical structure, allowing for efficient information retrieval.
Vector Store: Weaviate is used as the vector store to manage and retrieve the embeddings.
Query Embeddings: User queries are embedded and matched with document chunks to retrieve relevant information.
Response Generation: Retrieved content is generated and formatted as a response before being sent to the user via Slack.
Getting Started
Prerequisites
Python 3.8+
Docker (for Weaviate vector store)
Slack Workspace and a bot token
Django
Other dependencies listed in requirements.txt
Installation
Clone the Repository

bash
Copy code
git clone https://github.com/your-username/django-docs-bot.git
cd django-docs-bot
Install Dependencies

bash
Copy code
pip install -r requirements.txt
Start Weaviate with Docker

bash
Copy code
docker-compose up -d
Configure Environment Variables

Set up environment variables in a .env file for Slack and Weaviate configurations (see below).

Environment Variables
Create a .env file in the project root with the following configurations:

env
Copy code
SLACK_BOT_TOKEN=<your-slack-bot-token>
WEAVIATE_URL=http://localhost:8080
DJANGO_SECRET_KEY=<your-django-secret-key>
Usage
Run the Django Server

bash
Copy code
python manage.py runserver
Adding Bot to Slack Workspace

Invite the bot to your Slack workspace.
Interact with the bot by typing queries like /django-doc [your question].
Sample Query


text
Copy code
/django-doc What is a QuerySet?
Expected Response

The bot will retrieve relevant content from the Django documentation and display it in the Slack channel where the query was initiated.

Future Enhancements
Add Support for More Queries: Extend functionality to provide broader coverage of Django topics.
Advanced Chunking: Improve chunking to ensure even better context capture for multi-level topics.
Enhanced Response Generation: Fine-tune response templates and improve relevance ranking.
Contributing
Contributions are welcome! Please fork this repository, create a new branch, and submit a pull request. Follow the coding guidelines and include clear documentation for any additions or changes.