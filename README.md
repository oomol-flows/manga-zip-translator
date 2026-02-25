<div align=center>
	<h1>Manga ZIP Translator</h1>
	<p><a href="https://hub.oomol.com/package/manga-zip-translator?open=true" target="_blank"><img src="https://static.oomol.com/assets/button.svg" alt="Open in OOMOL Studio" /></a></p>
</div>

## Overview

Manga ZIP Translator is an automated tool that translates text in manga archives (ZIP files) into 26 target languages. It uses OCR technology to detect text in manga images, translates the text, and returns a new ZIP file with translated content.

## Features

### Supported Languages
- **Asian Languages**: Chinese (Simplified/Traditional), Japanese, Korean, Thai, Indonesian, Filipino
- **European Languages**: English, French, German, Italian, Spanish, Portuguese, Dutch, Czech, Polish, Hungarian, Romanian, Russian, Ukrainian, Croatian, Serbian, Montenegrin
- **Other Languages**: Arabic, Turkish, Vietnamese

### Main Components

#### 1. ZIP Translator Subflow
The main workflow that orchestrates the entire translation process:
- Validates ZIP file format
- Uploads file to cloud storage
- Submits translation task
- Polls for completion
- Returns translated ZIP download URL

**Inputs**:
- `file`: Local file path to manga ZIP archive (required)
- `target_lang`: Target language code, e.g., CHS for Chinese Simplified (required)

**Outputs**:
- `status`: Translation status (pending/processing/completed/failed)
- `result_zip_url`: Download URL of translated ZIP file

#### 2. Manga Zip Translate Task
Core translation task that interfaces with OOMOL Fusion API:
- Submits ZIP URL for translation
- Polls for task completion
- Returns translation results

**Inputs**:
- `zip_url`: Public URL of manga ZIP file (required)
- `target_lang`: Target language code (required)
- `wait_timeout`: Maximum wait time in seconds (default: 600)
- `poll_interval`: Status check interval in seconds (default: 5)

**Outputs**:
- `task_id`: Unique task identifier
- `status`: Task status
- `result_zip_url`: Translated ZIP download URL
- `total_pages`: Total pages detected
- `translated_pages`: Pages translated so far

#### 3. Check ZIP Format Task
Validates if a file is a valid ZIP archive by checking magic number signature.

**Inputs**:
- `url`: Local file path or remote URL (required)

**Outputs**:
- `is_zip`: Boolean indicating valid ZIP format
- `file_size`: File size in bytes
- `file_zip_path`: Local ZIP path (if local file)
- `file_zip_url`: Remote ZIP URL (if network URL)

## Usage

1. Open the ZIP Translator subflow
2. Select a manga ZIP file using the file picker
3. Choose target language from the dropdown
4. Run the workflow
5. Download the translated ZIP from the result URL

## Technical Notes

- Translation is performed by OOMOL Fusion API
- Supports both local files and remote URLs
- Includes retry logic for network failures
- Progress tracking available during translation