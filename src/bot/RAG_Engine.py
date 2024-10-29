import redis.client
from Document_processing import DocumentPreprocessing
from typing import List, Dict, Any
from vector_Store import IndexManager
import weaviate
import logging
import redis 
import hashlib
import json



class RagEngine:

    def __init__(self, redis_url: str ="redis://localhost:6379",
                 weaviate_url: str= "http://localhost:8080"):
        # self.Document_preprocessing= DocumentPreprocessing(redis_url) 
        self.Index= IndexManager(redis_url,weaviate_url)
        self.redis_client= redis.from_url(redis_url)
        self.doc_preprocess= self.Index.doc_processing
        self._setup_logging()

    
    def _setup_logging(self):
        self.logger = logging.getLogger("RAGQueryEngine")
        self.logger.setLevel(logging.INFO)
        handler = logging.FileHandler("query_engine.log")
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(handler)

    def _cache_query_result(self, query:str, results:List[Dict]):
        
        cache_key= f"query {hashlib.md5(query.encode()).hexdigest()}"
        self.redis_client.setex(cache_key, 3600, json.dumps(results))

    def _get_cached_query(self,query:str)-> List[Dict]:
        cached_key= f"query {hashlib.md5(query.encode()).hexdigest}"
        cached= self.redis_client(cached_key)
        return json.loads(cached_key) if  cached else None


    async def  query(self,query:str, k:int = 3)->List[Dict]:

        cached_result= self._get_cached_query(query=query)

        if cached_result:
            self.logger.info(f"Cache hit for query: {query[:50]}...")
            return cached_result
        
        query_vector= self.doc_preprocess.query_embedding(query)

        results = self.Index.client.query\
            .get(self.index_name, ["content", "section"])\
            .with_near_vector({"vector": query_vector})\
            .with_limit(k)\
            .with_additional(["certainty"])\
            .do()
        
        # Format results
        if results and "data" in results and "Get" in results["data"]:
            objects = results["data"]["Get"][self.index_name]
            return [(obj, obj.get("_additional", {}).get("certainty", 0)) 
                   for obj in objects]
        return []
    

if __name__ == "__main__":
    # Initialize the retriever
    retriever = RagEngine()
    retriever.Index.add_chunks()
    
    



    




    
