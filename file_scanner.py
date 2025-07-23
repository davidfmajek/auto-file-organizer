import os 
import yaml
from pathlib import Path
from datetime import datetime

#imports for previewing files
from PyPDF2 import PdfReader
from docx import Document
import pytesseract
from PIL import Image

#Function to Load the Yaml configiration file specifying folers to monitor and scan interval
def load_config(config_path: str = 'config.yaml') -> dict:
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

#function to read files and return a preview of their content
def preview_text(file_path: Path,max_chars:int = 500)-> str:
    try:
        #read file with errors to avoid decoiding issues
        with open(file_path,'r',errors='ignore')as f:
            return f.read(max_chars)
    except Exception:
        return ''
    
#Function to extract text preview from the first page of the pdf file
def preview_pdf(file_path:Path,max_chars:int = 500) -> str:
    try:
        reader = PdfReader(str(file_path)) #loads the PDF file
        text = ''
        #loop through the first 2 pages or until max_char is reached
        for page in reader.pages[:2]:
            text_chunk = page.extract_text() or ''
            text += text_chunk
            if len(text) >= max_chars:
                break
        return text[:max_chars]
    except Exception:
        return ''
    

#Function to exteacttext preview from a doxc file
def preview_docx(file_path:Path,max_chars: int = 500) -> str:
    try:
        doc = Document(str(file_path))  # loads the docx file
        #Join all the paragraphs text separated by lines(if any)
        full_text = '\n'.join([p.text for p in doc.paragraphs])
        return full_text[:max_chars]
    except Exception:
        return ''

#Function to preview image files using OCR
def preview_image(file_path: Path, max_chars: int = 500) -> str:
    try:
        img = Image.open(file_path) # loads the image file
        #using pytesseract to extract text from the image
        text = pytesseract.image_to_string(img) or ''
        return text[:max_chars]
    except Exception:
        return ''

#Function to retrive metadata and a short content preview for a specified file
def get_file_metadata(file_path: Path)-> dict:
    stat = file_path.stat()  # get file statistics
    #base metadata dictionary
    metadata = {
        'path': str(file_path),
        'name': file_path.name,
        'size_bytes': stat.st_size,
        'modified_time': datetime.fromtimestamp(stat.st_mtime).isoformat(),
        'created_time': datetime.fromtimestamp(stat.st_ctime).isoformat(),
        'preview': ''
    }
    ext = file_path.suffix.lower()  # get file extension
    #Determine the preview method based on file extension
    if ext in ['.txt', '.md', '.log']:
        metadata['preview'] = preview_text(file_path)
    elif ext == '.pdf':
        metadata['preview'] = preview_pdf(file_path)
    elif ext in ['.docx']:
        metadata['preview'] = preview_docx(file_path)
    elif ext in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']:
        metadata['preview'] = preview_image(file_path)
    return metadata


#Function to scan each folder in config and collect metadata for each file.
def scan_directories(config:dict) -> list:
    results = []
    #iterate over each directory to watch
    for folder in config.get('monitor_folders',[]):
        p = Path(folder).expanduser()
        if not p.exists():
            #skip if folder does not exist
            continue
        #iterate over items in the directory
        for file_path in p.iterdir():
            if file_path.is_file():
                #gets metadata and append to results
                results.append(get_file_metadata(file_path))
    return results

def main():
    #load settings from config.yaml
    config = load_config()
    #Perform directory scan
    files = scan_directories(config)
    #output each file's metadata
    for file in files:
        print(file)
    print(f"Scanned {len(files)} files.")


if __name__ == "__main__":
    main()
    print("File scanner initialized.")
