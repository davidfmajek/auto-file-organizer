from dotenv import load_dotenv
load_dotenv() 


import os
import json
import logging
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain_community.chat_models import ChatOpenAI       # community-maintained
from langchain.chains import LLMChain                        # still works for now
from langchain.prompts import ChatPromptTemplate
from typing import Optional

# Initialize LLM client (ensure OPENAI_API_KEY is set in environment)
llm = ChatOpenAI(
    temperature=0,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# Default prompt template for generating file suggestions
DEFAULT_PROMPT_TEMPLATE = """
You are an EXTREMELY AGGRESSIVE file organizer assistant. Your goal is to organize files into a clean, consistent structure.
Be PROACTIVE and CONFIDENT in your suggestions. Don't be afraid to make bold suggestions for renaming and organizing files.

RULES:
1. ALWAYS suggest a new filename and folder, even for well-named files
2. Use consistent naming: lowercase with underscores, no spaces or special characters
3. Group similar files in logical folders
4. Be more aggressive with temporary or poorly named files
5. Don't be conservative - better to suggest too much organization than too little

File metadata:
Name: {name}
Size (bytes): {size_bytes}
Created: {created_time}
Modified: {modified_time}
Content preview: {preview}

Return a JSON object with these keys:
- suggested_name: string (new filename, ALWAYS suggest a change)
- suggested_folder: string (folder path, ALWAYS suggest a folder)
- delete: boolean (true if file is clearly temporary, duplicate, or unnecessary)

Example outputs:
```json
{{
  "suggested_name": "resume_john_smith_2025.pdf",
  "suggested_folder": "documents/resumes",
  "delete": false
}}

{{
  "suggested_name": "screenshot_2025_07_18_1445.png",
  "suggested_folder": "media/screenshots/2025_07",
  "delete": false
}}
```
"""
def create_chain(custom_prompt: Optional[str] = None):
    """Create a new LLMChain with the specified or default prompt."""
    template = custom_prompt if custom_prompt else DEFAULT_PROMPT_TEMPLATE
    prompt = ChatPromptTemplate.from_template(template)
    return LLMChain(llm=llm, prompt=prompt)

# Default chain instance
default_chain = create_chain()

def should_delete_file(filename: str) -> bool:
    """Check if the file should be deleted based on its extension."""
    # List of file extensions to automatically delete
    delete_extensions = {
        '.dmg',     # macOS disk images
        '.pkg',     # macOS installer packages
        '.exe',     # Windows installers
        '.msi',     # Windows installer files
        '.app.zip'  # zipped macOS apps
    }
    
    # Check if the file extension matches any in our delete list
    filename_lower = filename.lower()
    return any(filename_lower.endswith(ext) for ext in delete_extensions)


def suggest_actions(file_meta: dict, custom_prompt: Optional[str] = None) -> dict:
    """
    Call the LLM chain with file metadata and parse its JSON response.
    Automatically deletes installer files and other specified types.

    :param file_meta: Metadata dict from file_scanner.get_file_metadata
    :returns: Parsed suggestions dict
    """
    # First check if this is a file type we want to delete
    filename = file_meta.get('name', '')
    if should_delete_file(filename):
        return {
            'suggested_name': filename,  # Keep original name for logging
            'suggested_folder': '',
            'delete': True
        }

    # Prepare input mapping for prompt for non-installer files
    inputs = {
        'name': filename,
        'size_bytes': file_meta.get('size_bytes', 0),
        'created_time': file_meta.get('created_time', ''),
        'modified_time': file_meta.get('modified_time', ''),
        'preview': file_meta.get('preview', '').replace('"', '\\"')
    }

    # Create chain with custom prompt if provided
    chain = create_chain(custom_prompt) if custom_prompt else default_chain
    
    # Generate suggestion
    try:
        raw = chain.run(**inputs)
        suggestion = json.loads(raw)
    except (json.JSONDecodeError, Exception) as e:
        logging.warning(f"Error generating suggestion: {str(e)}")
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
