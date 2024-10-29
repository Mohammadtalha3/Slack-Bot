from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import weaviate
import logging
import hashlib
import queue
import redis
import json
# import dotenv




class DocumentPreprocessing:

    def __init__(self, redis_url= 'redis://localhost:6379'):
        self.redis_client= redis.from_url(redis_url)
        self.model= SentenceTransformer('all-MiniLM-L6-v2')
        self.embedding=  queue.Queue()
        self.processing= False
        self._setup_logging()
    
    def _setup_logging(self):
        self.logger=  logging.getLogger("DocumentProcessor")
        self.logger.setLevel(logging.INFO)
        handler=  logging.FileHandler("document_processor.log")
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(handler)

    
    def _get_cache_key(self, content:str):

        return f" emb: {hashlib.md5(content.encode()).hexdigest()}"
    
    # This funtion will get you embeddings before that it checks if we have the key assigned to content is in cache or not
    def get_embedding(self, content:str )-> List[float]:

        cache_key= self._get_cache_key(content=content)
        cached= self.redis_client.get(cache_key)

        if cached:
            return json.loads(cached)
        
        embedding= self.model.encode(content).tolist()

        self.redis_client.setex(cache_key,86400, json.dump(embedding))

        return embedding
    
    def query_embedding(self, query:str):
        cache_key= self._get_cache_key(content=query)
        cached= self.redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
        
        query_embedding=self.model.encode(query).tolist()

        self.redis_client.setex(cache_key, 86400, json.dump(query_embedding))

        return query_embedding
    
        