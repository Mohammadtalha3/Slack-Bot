import weaviate
import redis
import uuid
from Document_processing import *


class IndexManager:

    def __init__(self, redis_url: str ="redis://localhost:6379",
                 weaviate_url: str= "http://localhost:8080" ):
        
        self.weavite_client= weaviate.Client(url=weaviate_url)
        self.redis_client=  redis.from_url(redis_url)
        self.doc_processing= DocumentPreprocessing(redis_url=redis_url)
        self.index_name="Documentation"
        self._setup_schema()
        self._setup_logging()

    
    def _setup_logging(self):
        self.logger = logging.getLogger('IndexManager')
        self.logger.setLevel(logging.INFO)
        handler= logging.FileHandler('index_manager.log')
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))

        self.logger.addHandler(handler)
    
    def _setup_schema(self):
        schema = {
            "class": self.index_name,
            "properties": [
                {
                    "name": "content",
                    "dataType": ["text"],
                },
                {
                    "name": "section",
                    "dataType": ["string"],
                },
                {
                    "name": "is_code",
                    "dataType": ["boolean"],
                },
                {
                    "name": "language",
                    "dataType": ["string"],
                },
                {
                    "name": "filename",
                    "dataType": ["string"],
                }
            ],
            "vectorizer": "none"}  # We'll manually add vectors
        
        try:
        
            self.weavite_client.schema.create_class(schema)
        except weaviate.exceptions.UnexpectedStatusCodeException:
            pass
    

    def process_chunk(self, chunk: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single document chunk with its metadata"""
        # print('this is the chunk in the process', chunk)
        return {
            "content": chunk["content"],
            "section": chunk["section"],
            "is_code": chunk.get("Code Info", {}).get("is_code", False),
            "language": chunk.get("Code Info", {}).get("language"),
            "filename": chunk.get("Code Info", {}).get("filename")
        }
        
    def add_chunks(self, chunks: List[Dict[str, Any]]) -> int:
        """Add document chunks to Weaviate with their embeddings"""
        # Process all chunks
        processed_chunks = [self.process_chunk(chunk) for chunk in chunks]

        print('this is the lenght of the processed chunks',len(processed_chunks))
        
        # Generate embeddings for all contents at once
        contents = [chunk["content"] for chunk in processed_chunks]
        embeddings = self.embeddings.embed_documents(contents)
        
        # Add chunks to Weaviate with their vectors
        with self.client.batch as batch:
            for chunk_data, vector in zip(processed_chunks, embeddings):
                batch.add_data_object(
                    data_object=chunk_data,
                    class_name=self.index_name,
                    uuid=uuid.uuid4(),
                    vector=vector
                )
                
        return len(processed_chunks)
    
    def search(self, query: str, k: int = 2, filters: Dict[str, Any] = None):
        """
        Search for relevant documents
        Args:
            query (str): The search query
            k (int): Number of results to return
            filters (dict): Optional filters (e.g., {"section": "2.1.1"})
        """
        # Generate query vector
        query_vector = self.embeddings.query_embd(query)
        
        # Prepare the query
        query_obj = (
            self.client.query
            .get(self.index_name, ["content","section"]) #, "is_code", "language", "filename","section"
            .with_near_vector({
                "vector": query_vector,
                "certainty": 0.7  # Adjust this threshold as needed
            })
            .with_limit(k)
        )
        
        # Add filters if provided
        if filters:
            where_filter = {"operator": "And", "operands": []}
            for key, value in filters.items():
                where_filter["operands"].append({
                    "path": [key],
                    "operator": "Equal",
                    "valueString": value
                })
            query_obj = query_obj.with_where(where_filter)
        
        # Execute the query
        result = query_obj.do()
        
        # Format results
        if result and "data" in result and "Get" in result["data"]:
            objects = result["data"]["Get"][self.index_name]
            return [(obj, obj.get("_additional", {}).get("certainty", 0)) 
                   for obj in objects]
        return []


