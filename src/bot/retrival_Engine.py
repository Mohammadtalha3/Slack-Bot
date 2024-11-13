# from Document_processing import DocumentPreprocessing
from sentence_transformers import SentenceTransformer
from typing import List,Dict, Any
import uuid


class OpenSourceEmbeddings:
    def __init__(self,model_name: str = "all-MiniLM-L6-v2"):
        self.model= SentenceTransformer(model_name)

    
    def embed_documents(self, full_text: list[str])-> List[List[str]]:
        return self.model.encode(full_text).tolist()

    def query_embd(self, query)-> List[float]:
        return self.model.encode(query) 

class DocumentRetriever:
    def __init__(self, weaviate_url: str = "http://localhost:8080"):
        self.embeddings =OpenSourceEmbeddings()
        import weaviate
        self.client = weaviate.Client(
            url=weaviate_url,
            additional_headers={
                "X-OpenAI-Api-Key": None
            }
        )
        self.index_name = "Documentation"
        self._create_schema()
    
    def _create_schema(self):
        """Create the Weaviate schema for documentation chunks"""
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
            "vectorizer": "none"  # We'll manually add vectors
        }
    
    def search(self, query: str, k: int = 3, filters: Dict[str, Any] = None):
        """
        Search for relevant documents with duplicate prevention
        Args:
            query (str): The search query
            k (int): Number of unique results to return
            filters (dict): Optional filters (e.g., {"section": "2.1.1"})
        """
        # Generate query vector
        query_vector = self.embeddings.query_embd(query)
        
        # Request more results than needed to account for potential duplicates
        search_k = k * 2
        
        # Prepare the query
        query_obj = (
            self.client.query
            .get(self.index_name, ["content", "section", "is_code", "language", "filename"]) #
            .with_hybrid(
                query= query,
                vector= query_vector,
                alpha=0.7,
                properties=['content', 'section']

            )
            .with_limit(search_k)  # Request more results
            .with_additional(["score","id"])  # Add ID for deduplication  , "id"
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
        
        # Format and deduplicate results
        unique_results = []
        seen_contents = set()
        
        if result and "data" in result and "Get" in result["data"]:
            objects = result["data"]["Get"][self.index_name]
            
            for obj in objects:
                content = obj["content"]
                if content not in seen_contents:
                    seen_contents.add(content)
                    certainty = obj.get("_additional", {}).get("certainty", 0)
                    unique_results.append((obj, certainty))
                    
                    # Break if we have enough unique results
                    if len(unique_results) >= k:
                        break
        
        # return unique_results[:k]

        return result

    def search_with_metadata(self, query: str, k: int = 3, filters: Dict[str, Any] = None):
        """
        Enhanced search that returns results with detailed metadata and prevents duplicates
        """
        results = self.search(query, k, filters)
        
        formatted_results = []
        for doc, score in results:
            formatted_results.append({
                'content': doc['content'],
                'metadata': {
                    'section': doc['section'],
                    'is_code': doc['is_code'],
                    'language': doc['language'],
                    'filename': doc['filename'],
                    'similarity_score': score
                }
            })
        
        return formatted_results
    

if __name__ == "__main__":
    retriever = DocumentRetriever()
    
    # Example search
    # query = " How can I see the raw SQL queries Django is running? "
    # query= " how forms  works in django "
    # query= "What are forms used for?"
    # query= "FAQ: Databases and models"
    # query= 'Does Django support NoSQL databases?'
    query= "Building a form "
    # results = retriever.search_with_metadata(query, k=3)
    search_results = retriever.search(query, k=3)

    print(search_results['data']['Get']['Documentation'][0])

    # from pprint import pprint

    # print('this is the search retriver', pprint(search_results[:1000]))
    # print(search_results['data']['Get']['Documentation'][1]['content'])







    

    
    # print("\nSearch Results:")
    # for idx, result in enumerate(results, 1):
    #     print(f"\nResult {idx}:")
    #     print(f"Score: {result['metadata']['similarity_score']:.4f}")
    #     print(f"Section: {result['metadata']['section']}")
    #     # print(f"iscode: {result['metadata']['is_code']}")
    #     # print(f"File: {result['metadata']['filename']}")
    #     print(f"Content Preview: {(result['content'])}...")
    #     print("-" * 80)
        
