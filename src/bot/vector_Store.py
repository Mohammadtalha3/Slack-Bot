import weaviate
import redis
import uuid
from Document_processing import *
from retrival_Engine import  OpenSourceEmbeddings
import numpy as np
import re
from typing import List,Tuple

class DocumentCleaner:
    def __init__(self):
        # Common patterns to remove
        self.patterns = {
            'page_numbers': r'^\d+$',  # Standalone page numbers
            'chapter_headers': r'^Chapter \d+\.\s.*$',  # Chapter headers like "Chapter 3. Using Django"
            'doc_headers': r'^Django Documentation, Release.*$',  # Documentation headers
            'footer_headers': r'.*Documentation, Release \d+\.\d+.*$',  # Footer headers
            'blank_lines': r'^\s*$',  # Empty or whitespace-only lines
            'repeated_dashes': r'-{3,}',  # Three or more dashes
            'page_breaks': r'\f',  # Form feed characters (page breaks)
            'section_page_numbers': r'^\d+\.\d+\.\s+.*\s+\d+$',  # Matches patterns like "3.4. Working with forms             341"
            'footer_titles': r'^\d+\.\d+\.*\s+[A-Za-z].*$',  # Matches section numbers with titles
            'isolated_titles': r'^[A-Z][a-z]+\s+[A-Za-z\s]+\d+$'
        }
        
        # Compile all patterns for efficiency
        self.compiled_patterns = {
            name: re.compile(pattern, re.MULTILINE) 
            for name, pattern in self.patterns.items()
        }

    def clean_chunk(self, text: str) -> str:
        """
        Clean a single chunk of text by removing headers, footers, and page numbers
        """
        if not text:
            return text

        # Split into lines to process line by line
        lines = text.split('\n')
        cleaned_lines = []
        
        for i, line in enumerate(lines):
            # Skip if line matches any of our patterns
            should_skip = any(
                pattern.match(line.strip())
                for pattern in self.compiled_patterns.values()
            )
            
            if not should_skip:
                # Additional cleaning steps
                line = self._clean_line(line)
                if line:  # Only add non-empty lines
                    cleaned_lines.append(line)

        # Join lines back together
        cleaned_text = '\n'.join(cleaned_lines)
        
        # Remove extra whitespace and normalize spacing
        cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)
        cleaned_text = cleaned_text.strip()
        
        return cleaned_text

    def _clean_line(self, line: str) -> str:
        """
        Clean a single line of text
        """
        # Remove form feeds and other special characters
        line = line.replace('\f', '')
        
        # Remove repeated whitespace
        line = re.sub(r'\s+', ' ', line)
        
        return line.strip()

    def process_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process a list of chunks, cleaning their content
        """
        cleaned_chunks = []
        
        for chunk in chunks:
            if 'content' in chunk:
                cleaned_content = self.clean_chunk(chunk['content'])

                
                
                # Only include chunk if it still has meaningful content after cleaning
                if cleaned_content and len(cleaned_content.strip()) > 50:  # Minimum content threshold
                    chunk['content'] = cleaned_content
                    cleaned_chunks.append(chunk)
        
        return cleaned_chunks




class IndexManager:

    def __init__(self, redis_url: str ="redis://localhost:6379",
                 weaviate_url: str= "http://localhost:8080" ):
        
        self.weavite_client= weaviate.Client(url=weaviate_url)
        self.redis_client=  redis.from_url(redis_url)
        self.doc_processing= DocumentPreprocessing(redis_url=redis_url)
        self.index_name="Documentation"
        # self._setup_schema()
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
            print('Schema Created')
        except weaviate.exceptions.UnexpectedStatusCodeException:
            pass
        return 'Schema has been created'
    

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
    def create_combined_text(self, chunk: Dict[str, Any]) -> str:
        """Create combined text from title and content for embedding"""
        combined_text = ""
        if chunk.get("title"):
            combined_text += f"Title: {chunk['title']}\n"
        if chunk.get("content"):
            combined_text += f"Content: {chunk['content']}"
        return combined_text.strip()

    def add_chunks(self, chunks: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[List[float]]]:
        """
        Add document chunks to Weaviate with their embeddings

        Args:
            chunks: List of document chunks

        Returns:
            Tuple containing:
            - List of processed chunks
            - List of embeddings
        """
        # Process all chunks
        processed_chunks = [self.process_chunk(chunk) for chunk in chunks]

        # Create combined text for each chunk (title + content)
        combined_texts = [self.create_combined_text(chunk) for chunk in processed_chunks]

        # Generate embeddings for combined texts
        embed = OpenSourceEmbeddings()
        embeddings = embed.embed_documents(combined_texts)

        # Add chunks to Weaviate with their vectors
        with self.weavite_client.batch as batch:
            for chunk_data, vector in zip(processed_chunks, embeddings):
                batch.add_data_object(
                    data_object=chunk_data,
                    class_name=self.index_name,
                    uuid=uuid.uuid4(),
                    vector=vector
                )

        return processed_chunks, embeddings
        
    # def add_chunks(self, chunks: List[Dict[str, Any]]) -> int:
    #     """Add document chunks to Weaviate with their embeddings"""
    #     # Process all chunks
    #     processed_chunks = [self.process_chunk(chunk) for chunk in chunks]

    #     # print('this is the lenght of the processed chunks',len(processed_chunks))
        
    #     # Generate embeddings for all contents at once
    #     contents = [chunk["content"] for chunk in processed_chunks]

    #     # print('This is the content ', contents)
    #     embed= OpenSourceEmbeddings()
    #     embeddings = embed.embed_documents(contents)

    #     # np.save('Data/pdf_embedding.npy', embeddings)
    #     # loaded_embeddings=np.load('Data/pdf_embedding.npy')
        
    #     # Add chunks to Weaviate with their vectors
    #     with self.weavite_client.batch as batch:
    #         for chunk_data, vector in zip(processed_chunks, embeddings):
    #             batch.add_data_object(
    #                 data_object=chunk_data,
    #                 class_name=self.index_name,
    #                 uuid=uuid.uuid4(),
    #                 vector=vector
    #             )
                
    #     return processed_chunks,embeddings

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


