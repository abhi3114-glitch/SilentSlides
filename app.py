"""
SilentSlides — AI Slide Deck Builder
Main Streamlit Application
"""

import streamlit as st
import os
import tempfile
from pathlib import Path
import logging

from src.ocr_engine import OCREngine, check_tesseract_installation
from src.text_processor import TextProcessor
from src.slide_generator import SlideGenerator
from config import THEMES_DIR

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="SilentSlides - AI Slide Deck Builder",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        color: #1a1a1a;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
        border-radius: 4px;
    }
    .info-box {
        padding: 1rem;
        background-color: #d1ecf1;
        border-left: 4px solid #0c5460;
        margin: 1rem 0;
        border-radius: 4px;
    }
    .warning-box {
        padding: 1rem;
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)


def check_dependencies():
    """Check if Tesseract is installed"""
    is_installed, message = check_tesseract_installation()
    return is_installed, message


def get_available_themes():
    """Get list of available themes"""
    themes = []
    if THEMES_DIR.exists():
        for theme_file in THEMES_DIR.glob("*.json"):
            themes.append(theme_file.stem)
    return themes if themes else ["clean"]


def save_uploaded_files(uploaded_files):
    """Save uploaded files to temporary directory"""
    temp_dir = tempfile.mkdtemp()
    file_paths = []
    
    for uploaded_file in uploaded_files:
        file_path = os.path.join(temp_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        file_paths.append(file_path)
    
    return file_paths


def main():
    # Header
    st.markdown('<div class="main-header">📊 SilentSlides</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">AI-Powered Slide Deck Builder from Screenshots</div>', unsafe_allow_html=True)
    
    # Check Tesseract installation
    tesseract_installed, tesseract_message = check_dependencies()
    
    if not tesseract_installed:
        st.markdown(f'<div class="warning-box"><strong>⚠️ Tesseract Not Found</strong><br>{tesseract_message}</div>', unsafe_allow_html=True)
        st.stop()
    else:
        st.markdown(f'<div class="success-box">✅ {tesseract_message}</div>', unsafe_allow_html=True)
    
    # Sidebar settings
    st.sidebar.header("⚙️ Settings")
    
    # Theme selector
    available_themes = get_available_themes()
    selected_theme = st.sidebar.selectbox(
        "Theme",
        available_themes,
        index=0
    )
    
    # OCR language
    ocr_language = st.sidebar.selectbox(
        "OCR Language",
        ["eng", "spa", "fra", "deu", "ita"],
        index=0,
        help="Language for text extraction"
    )
    
    # Advanced settings
    with st.sidebar.expander("Advanced Settings"):
        max_topics = st.slider("Max Topics", 3, 15, 10)
        max_bullets = st.slider("Max Bullets per Slide", 3, 8, 5)
        preprocess_images = st.checkbox("Preprocess Images", value=True, help="Apply image enhancement before OCR")
    
    # Main content
    st.markdown("### 📤 Upload Screenshots")
    st.markdown("Upload 5-10 screenshots containing text. Supported formats: PNG, JPG, JPEG")
    
    uploaded_files = st.file_uploader(
        "Choose screenshot files",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True,
        help="Drag and drop files here"
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} file(s) uploaded")
        
        # Preview thumbnails
        with st.expander("📸 Preview Uploaded Images"):
            cols = st.columns(min(len(uploaded_files), 4))
            for idx, uploaded_file in enumerate(uploaded_files):
                with cols[idx % 4]:
                    st.image(uploaded_file, caption=uploaded_file.name, use_container_width=True)
        
        # Generate button
        if st.button("🚀 Generate Slide Deck", type="primary", use_container_width=True):
            try:
                # Save uploaded files
                with st.spinner("Saving uploaded files..."):
                    file_paths = save_uploaded_files(uploaded_files)
                
                # Initialize engines
                with st.spinner("Initializing OCR and AI models..."):
                    ocr_engine = OCREngine(language=ocr_language)
                    text_processor = TextProcessor()
                    slide_generator = SlideGenerator(theme_name=selected_theme)
                
                # OCR extraction
                st.markdown("### 📝 Extracting Text from Screenshots")
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                results = []
                for i, file_path in enumerate(file_paths):
                    status_text.text(f"Processing {i+1}/{len(file_paths)}: {Path(file_path).name}")
                    result = ocr_engine.extract_text(file_path, preprocess=preprocess_images)
                    results.append(result)
                    progress_bar.progress((i + 1) / len(file_paths))
                
                progress_bar.empty()
                status_text.empty()
                
                # Display OCR results
                total_words = sum([r['word_count'] for r in results])
                avg_confidence = sum([r['confidence'] for r in results]) / len(results)
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Words Extracted", total_words)
                col2.metric("Avg. Confidence", f"{avg_confidence:.1f}%")
                col3.metric("Images Processed", len(results))
                
                # Show extracted text
                with st.expander("📄 View Extracted Text"):
                    combined_text = ocr_engine.get_combined_text(results)
                    st.text_area("Combined Text", combined_text, height=200)
                
                # Text processing and clustering
                st.markdown("### 🧠 Analyzing Topics")
                with st.spinner("Clustering sentences and extracting topics..."):
                    combined_text = ocr_engine.get_combined_text(results)
                    processed_data = text_processor.process_text(combined_text)
                
                # Display topics
                st.markdown(f"**Found {len(processed_data['topics'])} topics:**")
                
                for topic in processed_data['topics']:
                    with st.expander(f"📌 {topic['title']} ({topic['sentence_count']} sentences)"):
                        for bullet in topic['bullets']:
                            st.markdown(f"- {bullet}")
                
                # Generate slides
                st.markdown("### 📊 Generating Slides")
                with st.spinner("Creating PDF, PPTX, and Markdown slides..."):
                    output_files = slide_generator.generate_all(processed_data, base_name="slides")
                
                st.success("✅ Slide deck generated successfully!")
                
                # Download buttons
                st.markdown("### 💾 Download Your Slides")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    with open(output_files['pdf'], 'rb') as f:
                        st.download_button(
                            label="📄 Download PDF",
                            data=f.read(),
                            file_name=Path(output_files['pdf']).name,
                            mime="application/pdf",
                            use_container_width=True
                        )
                
                with col2:
                    with open(output_files['pptx'], 'rb') as f:
                        st.download_button(
                            label="📊 Download PPTX",
                            data=f.read(),
                            file_name=Path(output_files['pptx']).name,
                            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                            use_container_width=True
                        )
                
                with col3:
                    with open(output_files['md'], 'rb') as f:
                        st.download_button(
                            label="📝 Download Markdown",
                            data=f.read(),
                            file_name=Path(output_files['md']).name,
                            mime="text/markdown",
                            use_container_width=True
                        )
                
                # Summary
                st.markdown('<div class="info-box"><strong>📈 Generation Summary</strong><br>'
                           f'• {len(processed_data["topics"])} topics identified<br>'
                           f'• {processed_data["total_sentences"]} sentences analyzed<br>'
                           f'• {processed_data["slide_count"]} slides created<br>'
                           f'• Theme: {selected_theme}'
                           '</div>', unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                logger.exception("Error during processing")
    
    else:
        st.info("👆 Upload screenshots above to get started")
    
    # Footer
    st.markdown("---")
    st.markdown(
        '<div style="text-align: center; color: #666; font-size: 0.9rem;">'
        'SilentSlides — Local-first AI slide generation • No external APIs • Privacy-focused'
        '</div>',
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
