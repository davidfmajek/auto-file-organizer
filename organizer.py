from dotenv import load_dotenv
load_dotenv() 


import os
import json
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain_community.chat_models import ChatOpenAI       # community-maintained
from langchain.chains import LLMChain                        # still works for now
from langchain.prompts import ChatPromptTemplate

# Initialize LLM client (ensure OPENAI_API_KEY is set in environment)
llm = ChatOpenAI(
    temperature=0,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# Prompt template for generating file suggestions
template = """
You are a smart file organizer assistant. Based on the file metadata and content preview,
suggest a better filename, a target folder (relative to an organizational root), and
whether the file should be deleted.

File metadata:
Name: {name}
Size (bytes): {size_bytes}
Created: {created_time}
Modified: {modified_time}
Content preview: """ + """{preview}

Return a JSON object with keys:
- suggested_name: string (new filename)
- suggested_folder: string (folder path)
- delete: boolean (true if file is safe to delete)

Example output:
```json
{{
  "suggested_name": "Resume_2025_JohnSmith.pdf",
  "suggested_folder": "Documents/Resumes",
  "delete": false
}}
```
"""
# Create the prompt and chain for LLM processing
prompt = ChatPromptTemplate.from_template(template)
chain = LLMChain(llm=llm, prompt=prompt)

def suggest_actions(file_meta: dict) -> dict:
    """
    Call the LLM chain with file metadata and parse its JSON response.

    :param file_meta: Metadata dict from file_scanner.get_file_metadata
    :returns: Parsed suggestions dict
    """
    # Prepare input mapping for prompt
    inputs = {
        'name': file_meta.get('name', ''),
        'size_bytes': file_meta.get('size_bytes', 0),
        'created_time': file_meta.get('created_time', ''),
        'modified_time': file_meta.get('modified_time', ''),
        'preview': file_meta.get('preview', '').replace('"', '\\"')
    }

    # Generate suggestion
    raw = chain.run(**inputs)
    try:
        suggestion = json.loads(raw)
    except json.JSONDecodeError:
        # If parsing fails, return fallback structure
        suggestion = {
            'suggested_name': file_meta['name'],
            'suggested_folder': '',
            'delete': False
        }
    return suggestion

# Example usage if run directly
if __name__ == '__main__':
    # Sample metadata stub
    sample = {
        'name': 'untitled.pdf',
        'size_bytes': 123456,
        'created_time': '2025-07-22T12:00:00',
        'modified_time': '2025-07-22T12:30:00',
        'preview': 'John Smith – Senior Software Engineer Resume, 2025'
    }
    print(suggest_actions(sample))
