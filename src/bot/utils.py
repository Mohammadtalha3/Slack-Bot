# from transformers import DistilBertTokenizer, DistilBertForSequenceClassification, DistilBertForMaskedLM
# from langchain_core.prompts import PromptTemplate
# from .retrival_Engine import DocumentRetriever
# from langchain_ollama import OllamaLLM

# # from langchain_core.prompts import PromptTemplate
# class ResponseModel:
# # This function takes message and we responed with LLM generated response 
#     @classmethod
#     def response_model (cls,message, llm_model= 'llama2-7B'):
#          model= OllamaLLM(model=llm_model)
#          retriver= DocumentRetriever()
#          # print('This is the message in the response model', message)
#          print('Yes triggered by the slack_shared message')
#          relevant_chunk= retriver.search(message)
#          # print('This is the relevant chunk', relevant_chunk)
#          relevant_chunks=relevant_chunk['data']['Get']['Documentation'][0]['content']
#          print('this is the relevant chunk received', relevant_chunks)
#          # Using promptTemplate modules from the langchain 
#          # prompt_template="This is a Retrieval-Augmented Generation (RAG) system. Here is the user's query: {query}. Below is the relevant information retrieved: {chunk} also give the retrived chunk in relevant part and also rate the retrived chunk bassed on the query  and if retrived content has example liek html or code always add that in response."
#          prompt_template= 'This is the user query -> {query} detect the code and response base on the chunk recieved and the user query'
#          formatted_prompt = prompt_template.format(query=relevant_chunks)
#          return model.invoke(formatted_prompt)
    
    


from transformers import T5Tokenizer, T5ForConditionalGeneration
from .retrival_Engine import DocumentRetriever

class ResponseModel:
    @classmethod
    def response_model(cls, query, llm_model='t5-large'):
        # Initialize the T5 model and tokenizer
        tokenizer = T5Tokenizer.from_pretrained(llm_model)
        model = T5ForConditionalGeneration.from_pretrained(llm_model)
        
        
        # Initialize the document retriever
        retriever = DocumentRetriever()

        # Get relevant chunks based on the user's query
        relevant_chunk = retriever.search(query)
        relevant_chunks = relevant_chunk['data']['Get']['Documentation'][0]['content']

        # Format the input for T5 model
        input_text = f"Query: {query} \nRelevant information: {relevant_chunks} \n\nGenerate a response based on this if relevant chunk has code keep in the response."

        # Tokenize the input text
        inputs = tokenizer(input_text, return_tensors="pt", padding=True, truncation=True)

        # Generate a response
        outputs = model.generate(
            **inputs, 
            max_length=200,       # Max response length
            num_beams=5,          # Beam search for better quality
            early_stopping=True   # Stop early if a response is good enough
        )

        # Decode and return the generated response
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response
