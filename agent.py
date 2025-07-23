"""
agent.py

Defines a LangChain agent that assembles your file-organizer components
as tools. You can interactively ask it to scan, suggest, and (optionally) apply changes.
"""
import os
from dotenv import load_dotenv
load_dotenv()  # load OPENAI_API_KEY from .env

from langchain_community.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, Tool, AgentType
from file_scanner import load_config, scan_directories
from organizer import suggest_actions
from utils import apply_suggestion

# Load configuration
config = load_config()
root_folder = config.get('root_folder')

# Initialize LLM
api_key = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(
    temperature=0,
    openai_api_key=api_key
)

# Define tools for the agent
tools = [
    Tool(
        name="scan_files",
        func=lambda _: scan_directories(config),
        description="Scan configured directories and return a list of file metadata dicts."
    ),
    Tool(
        name="suggest_actions",
        func=lambda metadata: suggest_actions(metadata),
        description="Given file metadata, return a JSON dict with suggested_name, suggested_folder, and delete flag."
    ),
    Tool(
        name="apply_suggestion",
        func=lambda metadata, suggestion: apply_suggestion(
            metadata, suggestion, root_folder=root_folder, auto_confirm=True
        ),
        description="Apply a suggestion to the file system (rename/move/delete)."
    )
]

# Initialize a REACT-style zero-shot agent
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

if __name__ == '__main__':
    print("Welcome to the File Organizer Agent! Type 'exit' to quit.")
    while True:
        user_input = input(">> ")
        if user_input.lower() in ('exit', 'quit'):
            print("Goodbye!")
            break
        try:
            result = agent.run(user_input)
            print(result)
        except Exception as e:
            print(f"Error: {e}")
