# Auto File Organizer

An intelligent file organization tool that uses AI to automatically categorize, rename, and manage your files. The system can monitor specified folders and organize files based on their content and type.

## Features

- **AI-Powered Organization**: Uses OpenAI's API to analyze file contents and suggest better organization
- **Multiple File Type Support**: Handles text files, PDFs, Word documents, and images (with OCR)
- **Automatic Cleanup**: Can automatically delete temporary/installer files (.dmg, .pkg, .exe, .msi, .app.zip)
- **Flexible Monitoring**: Choose between one-time scans or continuous monitoring
- **Customizable**: Use default AI suggestions or provide your own custom prompt
- **Safe Operations**: Includes dry-run mode to preview changes before applying

## Prerequisites

- Python 3.7+
- Tesseract OCR (for image text recognition)
- OpenAI API key

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd auto_file_organizer
   ```

2. **Create and activate a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Tesseract OCR** (for image text recognition):
   - macOS: `brew install tesseract`
   - Ubuntu: `sudo apt install tesseract-ocr`
   - Windows: Download installer from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)

5. **Set up your OpenAI API key**:
   Create a `.env` file in the project root:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## Configuration

Edit `config.yaml` to customize the behavior:

```yaml
# Folders to monitor for files
monitor_folders:
  - ~/Downloads
  - ~/Documents
  - ~/Desktop

# Auto-apply all suggestions without confirmation
# Set to false to confirm each action
auto_confirm: true

# Where to place organized files
root_folder: /Users/your_username/Desktop/Organized
```

## Usage

### Basic Commands

1. **One-time scan** (preview changes):
   ```bash
   python main.py --once --dry-run
   ```

2. **One-time scan** (apply changes):
   ```bash
   python main.py --once
   ```

3. **Continuous monitoring** (real-time):
   ```bash
   python main.py --watch
   ```

### Advanced Options

- `--config PATH`: Specify a different config file (default: config.yaml)
- `--prompt-file PATH`: Use a custom prompt for file organization
- `--auto-confirm`: Auto-confirm all actions (overrides config)
- `--dry-run`: Preview changes without applying them

### Examples

1. **Preview organization without making changes**:
   ```bash
   python main.py --once --dry-run
   ```

2. **Use a custom prompt file**:
   ```bash
   python main.py --once --prompt-file my_prompt.txt
   ```

3. **Run in watch mode with auto-confirm**:
   ```bash
   python main.py --watch --auto-confirm
   ```

## Custom Prompts

Create a text file with your custom prompt to control how files are organized. The prompt should instruct the AI on how to rename and categorize files.

Example `my_prompt.txt`:
```
You are a file organizer. Follow these rules:
1. Rename files to be lowercase with underscores
2. Organize by file type and year-month
3. Create these main folders:
   - documents/
   - images/
   - archives/
   - media/
4. Be aggressive with organizing - don't leave files in the root

Example output:
{
  "suggested_name": "resume_2025_john_smith.pdf",
  "suggested_folder": "documents/resumes/2025_07",
  "delete": false
}
```

## File Types Handled

- **Automatically Deleted**:
  - `.dmg` (macOS disk images)
  - `.pkg` (macOS installer packages)
  - `.exe` (Windows installers)
  - `.msi` (Windows installer files)
  - `.app.zip` (zipped macOS apps)

- **Content Analysis**:
  - Text files (`.txt`, `.md`, `.log`)
  - PDF documents
  - Word documents (`.docx`)
  - Images with text (using OCR)

## Troubleshooting

1. **Files not being moved**:
   - Check that the `root_folder` in config.yaml exists and is writable
   - Ensure you have the necessary permissions

2. **OCR not working**:
   - Verify Tesseract OCR is installed and in your system PATH
   - Check that image files are not corrupted

3. **API errors**:
   - Verify your OpenAI API key is set in the .env file
   - Check your internet connection
   - Ensure you have sufficient API credits
