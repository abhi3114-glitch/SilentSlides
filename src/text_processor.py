"""
Text Processing and Clustering Module
Uses SentenceTransformers for semantic analysis and clustering
"""

import re
import numpy as np
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
try:
    import hdbscan
    HDBSCAN_AVAILABLE = True
except ImportError:
    HDBSCAN_AVAILABLE = False
from sklearn.metrics.pairwise import cosine_similarity
import logging

from config import (
    SENTENCE_TRANSFORMER_MODEL, 
    MIN_CLUSTER_SIZE, 
    CLUSTERING_METHOD,
    MAX_TOPICS,
    MAX_BULLETS_PER_SLIDE
)

logger = logging.getLogger(__name__)


class TextProcessor:
    """Text analysis and topic extraction using semantic embeddings"""
    
    def __init__(self, model_name: str = SENTENCE_TRANSFORMER_MODEL):
        logger.info(f"Loading SentenceTransformer model: {model_name}")
        self.model = SentenceTransformer(model_name)
        logger.info("Model loaded successfully")
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        return text.strip()
    
    def split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        # Clean and filter
        sentences = [s.strip() for s in sentences if s.strip()]
        # Filter out very short sentences (likely noise)
        sentences = [s for s in sentences if len(s.split()) >= 3]
        return sentences
    
    def generate_embeddings(self, sentences: List[str]) -> np.ndarray:
        """Generate semantic embeddings for sentences"""
        if not sentences:
            return np.array([])
        embeddings = self.model.encode(sentences, show_progress_bar=False)
        return embeddings
    
    def cluster_sentences(
        self, 
        sentences: List[str], 
        embeddings: np.ndarray,
        n_clusters: int = None
    ) -> Dict[int, List[str]]:
        """
        Cluster sentences by semantic similarity
        
        Args:
            sentences: List of sentences
            embeddings: Sentence embeddings
            n_clusters: Number of clusters (auto-detected if None)
        
        Returns:
            Dict mapping cluster_id -> list of sentences
        """
        if len(sentences) < 2:
            return {0: sentences}
        
        # Auto-determine number of clusters
        if n_clusters is None:
            n_clusters = min(MAX_TOPICS, max(2, len(sentences) // 5))
        
        # Use HDBSCAN if available, otherwise KMeans
        if CLUSTERING_METHOD == "hdbscan" and HDBSCAN_AVAILABLE:
            clusterer = hdbscan.HDBSCAN(
                min_cluster_size=MIN_CLUSTER_SIZE,
                metric='euclidean'
            )
            labels = clusterer.fit_predict(embeddings)
        else:
            # KMeans fallback
            n_clusters = min(n_clusters, len(sentences))
            clusterer = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            labels = clusterer.fit_predict(embeddings)
        
        # Group sentences by cluster
        clusters = {}
        for idx, label in enumerate(labels):
            if label == -1:  # Noise in HDBSCAN
                label = max(labels) + 1  # Put noise in separate cluster
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(sentences[idx])
        
        return clusters
    
    def generate_topic_title(self, sentences: List[str], embeddings: np.ndarray) -> str:
        """
        Generate a title for a topic cluster
        Uses the most central sentence (closest to centroid)
        """
        if not sentences:
            return "Topic"
        
        if len(sentences) == 1:
            return self._shorten_sentence(sentences[0])
        
        # Find centroid
        centroid = embeddings.mean(axis=0).reshape(1, -1)
        
        # Find sentence closest to centroid
        similarities = cosine_similarity(embeddings, centroid).flatten()
        best_idx = similarities.argmax()
        
        # Shorten if needed
        title = self._shorten_sentence(sentences[best_idx])
        return title
    
    def _shorten_sentence(self, sentence: str, max_words: int = 6) -> str:
        """Shorten a sentence for use as title"""
        words = sentence.split()
        if len(words) <= max_words:
            return sentence.rstrip('.,!?')
        
        # Take first N words and add ellipsis
        return ' '.join(words[:max_words]) + '...'
    
    def rank_bullets(self, sentences: List[str], embeddings: np.ndarray, max_bullets: int = MAX_BULLETS_PER_SLIDE) -> List[str]:
        """
        Rank and select most important sentences as bullet points
        Uses diversity and centrality
        """
        if len(sentences) <= max_bullets:
            return sentences
        
        # Calculate centroid
        centroid = embeddings.mean(axis=0).reshape(1, -1)
        
        # Score by centrality (similarity to centroid)
        centrality_scores = cosine_similarity(embeddings, centroid).flatten()
        
        # Select top sentences
        top_indices = centrality_scores.argsort()[-max_bullets:][::-1]
        
        return [sentences[i] for i in top_indices]
    
    def process_text(self, text: str) -> Dict:
        """
        Main processing pipeline
        
        Args:
            text: Raw text from OCR
        
        Returns:
            Processed data with topics and slides
        """
        # Clean text
        cleaned = self.clean_text(text)
        
        # Split into sentences
        sentences = self.split_sentences(cleaned)
        
        if not sentences:
            return {
                'topics': [],
                'slide_count': 0,
                'total_sentences': 0
            }
        
        # Generate embeddings
        embeddings = self.generate_embeddings(sentences)
        
        # Cluster sentences
        clusters = self.cluster_sentences(sentences, embeddings)
        
        # Generate topics
        topics = []
        for cluster_id, cluster_sentences in clusters.items():
            # Get embeddings for this cluster
            cluster_indices = [i for i, s in enumerate(sentences) if s in cluster_sentences]
            cluster_embeddings = embeddings[cluster_indices]
            
            # Generate title
            title = self.generate_topic_title(cluster_sentences, cluster_embeddings)
            
            # Rank bullets
            bullets = self.rank_bullets(cluster_sentences, cluster_embeddings)
            
            topics.append({
                'id': cluster_id,
                'title': title,
                'bullets': bullets,
                'sentence_count': len(cluster_sentences)
            })
        
        # Sort topics by sentence count (most important first)
        topics.sort(key=lambda t: t['sentence_count'], reverse=True)
        
        return {
            'topics': topics,
            'slide_count': len(topics) + 2,  # +1 for title, +1 for summary
            'total_sentences': len(sentences)
        }
