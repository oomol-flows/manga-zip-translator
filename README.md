<div align=center>
	<h1>Comic Package Translation</h1>
	<p><a href="https://hub.oomol.com/package/manga-zip-translator?open=true" target="_blank"><img src="https://static.oomol.com/assets/button.svg" alt="Open in OOMOL Studio" /></a></p>
</div>

## Project Overview

Automatically translate manga ZIP archives to 26 target languages with OCR technology and optional colorization. This service uses OOMOL internal tokens for billing, with the billing subject as `manga-zip-translate`. Current pricing is 500 pages per token, with double metering when colorization is enabled.

The translation process uses a small amount of AI for translation and records the associated costs. Note that the 500 pages/token pricing may be subject to change in the future.

## Block Capabilities

### Local File Zip Translator
Translate local manga ZIP files. Uploads file, validates format, submits for translation, and returns download URL. Best for OOMOL Studio use.

### URL Zip Translator
Translate manga ZIP from URL. Validates URL, submits for translation, and returns download URL. Best for web or API integration.

### Check Zip Format
Validate if a local file or remote URL is a valid ZIP archive by checking magic number signature.

## Block Combination Suggestions

- Use **Local File Zip Translator** when working in OOMOL Studio with local files
- Use **URL Zip Translator** when integrating with web applications or APIs
- Use **Check Zip Format** to validate files before translation

## Basic Usage

1. Select a translation block based on your input source (local file or URL)
2. Choose target language from 26 supported languages
3. Enable colorization option if needed for black-and-white manga
4. Run the workflow and download translated ZIP

## Examples

**Local file translation:**
- Input: Select manga ZIP file using file picker
- Target language: CHS (Chinese Simplified)
- Output: Download URL of translated ZIP

**URL translation:**
- Input: Public URL of manga ZIP file
- Target language: ENG (English)
- Output: Download URL of translated ZIP