import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import pickle
import os
from typing import List, Dict, Tuple

class VectorService:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.dimension = 384  # Dimension of the embedding model
        self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine similarity
        self.articles_metadata = []  # Store article metadata
        self.index_file = "faiss_index.bin"
        self.metadata_file = "articles_metadata.pkl"
        self.load_index()
    
    def load_index(self):
        """Load existing FAISS index and metadata if they exist"""
        if os.path.exists(self.index_file) and os.path.exists(self.metadata_file):
            self.index = faiss.read_index(self.index_file)
            with open(self.metadata_file, 'rb') as f:
                self.articles_metadata = pickle.load(f)
    
    def save_index(self):
        """Save FAISS index and metadata to disk"""
        faiss.write_index(self.index, self.index_file)
        with open(self.metadata_file, 'wb') as f:
            pickle.dump(self.articles_metadata, f)
    
    def add_articles(self, articles: List[Dict]):
        """Add articles to the vector store"""
        for article in articles:
            # Create embedding
            text = f"{article['title']} {article['content']}"
            embedding = self.model.encode([text])
            
            # Normalize for cosine similarity
            faiss.normalize_L2(embedding)
            
            # Add to index
            self.index.add(embedding)
            
            # Store metadata
            self.articles_metadata.append({
                'id': article.get('id'),
                'title': article['title'],
                'url': article['url'],
                'source': article['source'],
                'category': article['category'],
                'published_at': article.get('published_at')
            })
        
        self.save_index()
    
    def search_similar_articles(self, query: str, k: int = 10, interests: List[str] = None) -> List[Dict]:
        """Search for similar articles based on query and user interests"""
        # Create query embedding
        query_embedding = self.model.encode([query])
        faiss.normalize_L2(query_embedding)
        
        # Search in FAISS
        scores, indices = self.index.search(query_embedding, min(k * 2, self.index.ntotal))
        
        # Filter and rank results
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= len(self.articles_metadata):
                continue
                
            article = self.articles_metadata[idx]
            
            # Filter by interests if provided
            if interests and article['category'] not in interests:
                continue
            
            article['similarity_score'] = float(score)
            results.append(article)
            
            if len(results) >= k:
                break
        
        return results
    
    def get_trending_topics(self, interests: List[str] = None) -> List[str]:
        """Get trending topics from stored articles"""
        # Simple implementation - in production, use more sophisticated topic modeling
        categories = {}
        for article in self.articles_metadata:
            if interests and article['category'] not in interests:
                continue
            
            category = article['category']
            categories[category] = categories.get(category, 0) + 1
        
        # Sort by frequency and return top topics
        trending = sorted(categories.items(), key=lambda x: x[1], reverse=True)
        return [topic for topic, count in trending[:5]]
    
# Global instance
vector_service = VectorService()
