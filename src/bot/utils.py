from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from retrival_Engine import DocumentRetriever


class ResponseModel:

# This function takes message and we responed with LLM generated response 
    def response_model (self,message, llm_model= 'llama3.2'):
        model= OllamaLLM(model=llm_model)
        retriver= DocumentRetriever()

        relevant_chunk= retriver.search_with_metadata(message)

        # Using promptTemplate modules from the langchain 
        prompt_template="This is a Retrieval-Augmented Generation (RAG) system. Here is the user's query: {query}. Below is the relevant information retrieved: {chunk} also give the retrived chunk in response."

        formatted_prompt = prompt_template.format(query=message,chunk=relevant_chunk)

        return model.invoke(formatted_prompt)
    

data=ResponseModel()
dt2=data.response_model(message='How to use templates in django?')

print(dt2)
    

    





    
    

