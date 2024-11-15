import redis.client
from Document_processing import DocumentPreprocessing
from typing import List, Dict, Any
from vector_Store import IndexManager
import pdfplumber
import weaviate
import logging
import redis 
import hashlib
import json
import re
from typing import List, Dict
from datetime import datetime
from vector_Store import DocumentCleaner




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
    
  

    def detect_code_blocks(self,text: str) -> Dict:
        """
        Detects if a text contains code and returns code information.
        """
        # Common code indicators
        code_patterns = [
            (r'class\s+\w+\(.*\):', 'python'),  # Python class definition
            (r'def\s+\w+\(.*\):', 'python'),    # Python function definition
            (r'from\s+[\w.]+\s+import', 'python'),  # Python import
            (r'import\s+[\w.]+', 'python'),     # Python import
            (r'@\w+', 'python'),                # Python decorator
            (r'^\s*public\s+class\s+\w+', 'java'),  # Java class
            (r'function\s+\w+\(.*\)', 'javascript'),  # JavaScript function
        ]
    
        # Detect listing format
        listing_match = re.search(r'Listing\s+(\d+):\s*(.*?)$', text, re.MULTILINE)

        # print('these are code patterns ', listing_match)
        
        is_code = False
        code_info = {
            'is_code': False,
            'language': None,
            'listing_number': None,
            'filename': None
        }
        
        # Check for listing format
        if listing_match:
            code_info['is_code'] = True
            code_info['listing_number'] = listing_match.group(1)
            code_info['filename'] = listing_match.group(2)
            
            # Detect language from filename
            if code_info['filename']:
                if '.py' in code_info['filename']:
                    code_info['language'] = 'python'
                elif '.js' in code_info['filename']:
                    code_info['language'] = 'javascript'
                elif '.java' in code_info['filename']:
                    code_info['language'] = 'java'
            
            return code_info
        
        # Check for code patterns
        for pattern, language in code_patterns:
            if re.search(pattern, text, re.MULTILINE):
                code_info['is_code'] = True
                code_info['language'] = language
                break
                
        return code_info   


    def chunk_document(self,document: str) -> List[Dict]:
        """
        Chunks a document into sections while preserving context and adding metadata.
        """
      
        chunks = []
        current_chunk = {
            'metadata': {
                'chunk_type': '',
                'hierarchy_level': 0,
                'previous_section': '',
                'next_section': '',
                'word_count': 0,
                'char_count': 0,
                'created_at': datetime.now().isoformat(),
                'parent_section': '',
                'contains_code': False,
                'code_info': None
            },
            'section': '',
            'title': '',
            'content': ''
        }
      
        # Patterns for matching sections, standalone page numbers, and chapter titles
        section_pattern = re.compile(r"^(\d+(\.\d+)*)\s+([^\n]+)")
        page_number_pattern = re.compile(r"^\d+$")
        chapter_pattern = re.compile(r"^\s*CHAPTER\s*$", re.IGNORECASE)
      
        lines = document.splitlines()
        i = 0
      
        while i < len(lines):
            line = lines[i].strip()
          
            if not line:
                i += 1
                continue
              
            chapter_match = chapter_pattern.match(line)
            if chapter_match:
                if current_chunk['content'] or current_chunk['title']:
                    # Check for code in current chunk before appending
                    code_info = self.detect_code_blocks(current_chunk['content'])
                    current_chunk['metadata']['contains_code'] = code_info['is_code']
                    current_chunk['metadata']['code_info'] = code_info if code_info['is_code'] else None
                  
                    # Add other metadata
                    current_chunk['metadata']['word_count'] = len(current_chunk['content'].split())
                    current_chunk['metadata']['char_count'] = len(current_chunk['content'])
                    chunks.append(current_chunk)
                  
                    if len(chunks) > 0:
                        chunks[-1]['metadata']['next_section'] = 'CHAPTER'
                        current_chunk['metadata']['previous_section'] = chunks[-1]['section']
                  
                current_chunk = {
                    'metadata': {
                        'chunk_type': 'chapter',
                        'hierarchy_level': 0,
                        'previous_section': '',
                        'next_section': '',
                        'word_count': 0,
                        'char_count': 0,
                        'created_at': datetime.now().isoformat(),
                        'parent_section': '',
                        'contains_code': False,
                        'code_info': None
                    },
                    'section': '',
                    'title': '',
                    'content': ''
                }
              
                # Rest of your chapter handling code...
                chapter_text = line
                i += 1
              
                while i < len(lines):
                    next_line = lines[i].strip()
                    if next_line:
                        current_chunk['section'] = f"{chapter_text} {next_line}"
                        current_chunk['metadata']['chunk_type'] = 'chapter'
                        i += 1
                      
                        while i < len(lines):
                            next_line = lines[i].strip()
                            if next_line:
                                current_chunk['title'] = next_line
                                i += 1
                                break
                            i += 1
                        break
                    i += 1
                continue
                  
            section_match = section_pattern.match(line)
            if section_match:
                if "." in section_match.group(1):
                    if current_chunk['content'] or current_chunk['title']:
                        # Check for code in current chunk before appending
                        code_info = self.detect_code_blocks(current_chunk['content'])
                        current_chunk['metadata']['contains_code'] = code_info['is_code']
                        current_chunk['metadata']['code_info'] = code_info if code_info['is_code'] else None
                      
                        current_chunk['metadata']['word_count'] = len(current_chunk['content'].split())
                        current_chunk['metadata']['char_count'] = len(current_chunk['content'])
                        chunks.append(current_chunk)
                      
                        if len(chunks) > 0:
                            chunks[-1]['metadata']['next_section'] = section_match.group(1)                          
                    current_chunk = {
                        'metadata': {
                            'chunk_type': 'section',
                            'hierarchy_level': len(section_match.group(1).split('.')),
                            'previous_section': chunks[-1]['section'] if chunks else '',
                            'next_section': '',
                            'word_count': 0,
                            'char_count': 0,
                            'created_at': datetime.now().isoformat(),
                            'parent_section': '.'.join(section_match.group(1).split('.')[:-1]),
                            'contains_code': False,
                            'code_info': None
                        },
                        'section': section_match.group(1),
                        'title': section_match.group(3),
                        'content': ''
                    }
          
            elif page_number_pattern.match(line):
                pass
            else:
                if current_chunk['content']:
                    current_chunk['content'] += "\n" + line
                else:
                    current_chunk['content'] = line
                  
            i += 1
          
        # Process the final chunk
        if current_chunk['content'] or current_chunk['title']:
            code_info = self.detect_code_blocks(current_chunk['content'])
            current_chunk['metadata']['contains_code'] = code_info['is_code']
            current_chunk['metadata']['code_info'] = code_info if code_info['is_code'] else None
          
            current_chunk['metadata']['word_count'] = len(current_chunk['content'].split())
            current_chunk['metadata']['char_count'] = len(current_chunk['content'])
            chunks.append(current_chunk)
      
        return chunks

    
            





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
    
    def Data_loading(self):

        document_path= 'Data\django.pdf'

        print('working of loading data...')

        with pdfplumber.open(document_path) as doc:
            full_text=''
            for page in doc.pages:
                full_text += page.extract_text(x_tolerance=1, y_tolerance=1, layout=True)
            
            return full_text
    

if __name__ == "__main__":
    # Initialize the retriever
#     retriever = RagEngine()
#     cleaner= DocumentCleaner()
    
#     # loading Data 
#     data_loaded=retriever.Data_loading()
# # Calling Chunking function
#     chunks = retriever.chunk_document(data_loaded)
    retriever = RagEngine()
    data_loaded = retriever.Data_loading()
    chunks = retriever.chunk_document(data_loaded)

    # Storing Chunks in weaviate( vector Store)
    Indexing=retriever.Index.add_chunks(chunks)

    print(Indexing)


# import json

# # Convert chunks to a list of dictionaries if they are not already
# with open('chunks.json', 'w') as file:
#     json.dump(chunks, file, indent=4)


    
    


for chunk in chunks:  
    print(f"metadata {chunk['metadata']}")
    print(f"Section {chunk['section']}")
    print(f"Content {chunk['content'][:100]}")
