# SilentSlides — AI Slide Deck Builder

Transform screenshots into professional slide decks using local OCR and AI-powered topic extraction. No external APIs, fully privacy-focused.

## Features

**Screenshot Processing**
- Drag-and-drop multiple screenshots (PNG, JPG, JPEG)
- Automatic OCR text extraction using Tesseract
- Image preprocessing for enhanced accuracy

**AI-Powered Analysis**
- Semantic sentence clustering using SentenceTransformers
- Automatic topic identification and grouping
- Smart bullet point extraction and ranking
- CPU-friendly, runs entirely locally

**Multi-Format Export**
- **PDF**: Professional slide decks with ReportLab
- **PPTX**: PowerPoint-compatible presentations
- **Markdown**: Clean markdown slides for web/GitHub

**Theme System**
- Clean minimalist theme
- Modern dark theme
- Professional corporate theme
- Customizable layouts and colors

## Installation

### Prerequisites

**1. Tesseract OCR**

SilentSlides requires Tesseract OCR to be installed on your system:

**Windows:**
```bash
# Download installer from:
# https://github.com/UB-Mannheim/tesseract/wiki

# Add Tesseract to your PATH or the app will auto-detect common installation paths
```

**macOS:**
```bash
brew install tesseract
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

Verify installation:
```bash
tesseract --version
```

**2. Python 3.8+**

Ensure you have Python 3.8 or higher installed. Python 3.11 is recommended.

### Setup

1. **Clone this repository**

```bash
git clone https://github.com/abhi3114-glitch/SilentSlides.git
cd SilentSlides
```

2. **Create virtual environment (recommended)**

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

3. **Install Python dependencies**

```bash
pip install -r requirements.txt
```

On first run, SentenceTransformers will download the AI model (~80MB). This is cached locally for future use.

## Usage

### Quick Start

1. **Launch the application:**

```bash
streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`

2. **Upload screenshots:**
   - Click the upload area or drag and drop 5-10 screenshots
   - Supported formats: PNG, JPG, JPEG

3. **Configure settings (optional):**
   - Select theme (clean, modern_dark, professional)
   - Choose OCR language
   - Adjust max topics and bullets per slide

4. **Generate slides:**
   - Click "Generate Slide Deck"
   - Wait for processing (OCR → AI analysis → slide generation)
   - Download in your preferred format (PDF, PPTX, Markdown)

### Example Workflow

```
1. Take screenshots of:
   - Documentation pages
   - Article summaries
   - Meeting notes
   - Lecture slides
   
2. Upload to SilentSlides

3. AI extracts text and identifies key topics

4. Download professional slide deck in seconds
```

## Project Structure

```
SilentSlides/
├── app.py                      # Main Streamlit application
├── config.py                   # Configuration and Tesseract detection
├── requirements.txt            # Python dependencies
├── README.md                   # This file
│
├── src/
│   ├── ocr_engine.py          # Tesseract OCR wrapper
│   ├── text_processor.py      # SentenceTransformers + clustering
│   └── slide_generator.py     # PDF/PPTX/Markdown exporters
│
├── themes/
│   ├── clean.json             # Minimalist theme
│   ├── modern_dark.json       # Dark mode theme
│   └── professional.json      # Corporate theme
│
└── output/                     # Generated slides (auto-created)
```

## Technical Details

### OCR Pipeline

1. **Image Preprocessing:**
   - Grayscale conversion
   - Contrast enhancement
   - Noise reduction via median filter
   - Sharpness adjustment

2. **Text Extraction:**
   - Tesseract OCR with confidence scoring
   - Multi-language support
   - Batch processing with progress tracking

### Text Analysis

1. **Sentence Segmentation:**
   - Smart sentence splitting
   - Noise filtering (removes short fragments)

2. **Semantic Clustering:**
   - SentenceTransformer embeddings (all-MiniLM-L6-v2)
   - HDBSCAN clustering (or K-Means fallback)
   - Automatic topic count determination

3. **Content Extraction:**
   - Centroid-based title generation
   - Diversity-aware bullet selection
   - Importance ranking by centrality

### Slide Generation

- **PDF**: ReportLab with custom paragraph styles
- **PPTX**: python-pptx with precise positioning
- **Markdown**: GitHub-flavored markdown with slide separators

## Configuration

### Theme Customization

Create custom themes by adding JSON files to `themes/`:

```json
{
  "name": "my_theme",
  "description": "Custom theme description",
  "colors": {
    "background": "#FFFFFF",
    "title": "#1a1a1a",
    "text": "#333333",
    "accent": "#0066cc"
  },
  "fonts": {
    "title": "Helvetica-Bold",
    "heading": "Helvetica-Bold",
    "body": "Helvetica"
  },
  "sizes": {
    "title": 28,
    "heading": 24,
    "body": 14
  }
}
```

### Advanced Settings

Edit `config.py` to customize:

- `SENTENCE_TRANSFORMER_MODEL`: Change AI model
- `MIN_CLUSTER_SIZE`: Minimum sentences per topic
- `MAX_TOPICS`: Maximum number of topics
- `MAX_BULLETS_PER_SLIDE`: Bullets per slide
- `OCR_CONFIG`: Tesseract parameters

## Troubleshooting

### Tesseract Not Found

**Issue:** `Tesseract not found` error on startup

**Solution:**
1. Verify installation: `tesseract --version`
2. Add Tesseract to PATH
3. Or edit `config.py` to set `TESSERACT_CMD` manually

### Poor OCR Accuracy

**Issue:** Text extraction quality is low

**Solutions:**
- Enable "Preprocess Images" in settings
- Use higher resolution screenshots
- Ensure text is clearly visible (not blurry)
- Try different OCR language settings

### Low Memory / Slow Performance

**Issue:** Processing takes too long or runs out of memory

**Solutions:**
- Process fewer screenshots at once (5-7 recommended)
- Use smaller images (resize before upload)
- Close other applications to free RAM
- The app is designed for CPU-only operation (no GPU needed)

### Model Download Fails

**Issue:** SentenceTransformer model won't download

**Solution:**
- Check internet connection (only needed on first run)
- Model is cached in `~/.cache/torch/sentence_transformers/`
- Manually download and place in cache directory if firewall blocks

## Performance Benchmarks

Typical performance on a modern laptop (tested on i5 CPU, 8GB RAM):

- **OCR per image**: 1-3 seconds
- **Clustering 100 sentences**: 3-5 seconds
- **Full pipeline (10 screenshots)**: 30-60 seconds
- **Memory usage**: ~500MB-1GB peak

## Privacy & Security

**Fully Local Processing**
- No external API calls
- No data sent to cloud services
- All processing happens on your machine

**No Data Retention**
- Uploaded images are stored in temporary directory
- Cleaned up automatically after processing
- Generated output is saved only to `output/` folder

## Dependencies

- **streamlit**: Web UI framework
- **pytesseract**: Tesseract OCR wrapper
- **Pillow**: Image processing
- **sentence-transformers**: Semantic embeddings
- **scikit-learn**: Clustering algorithms
- **python-pptx**: PowerPoint generation
- **reportlab**: PDF generation

## License

This project is open source and available for educational and commercial use.

## Contributing

Contributions welcome! Areas for improvement:

- Additional theme templates
- More export formats (Google Slides, Keynote)
- Advanced layout algorithms
- Multi-language UI
- Image/diagram extraction from screenshots

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Verify all dependencies are installed correctly
3. Review logs in the Streamlit console for detailed error messages

---

Built with Python, Tesseract, and SentenceTransformers
