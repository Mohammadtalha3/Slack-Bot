from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from .retrival_Engine import DocumentRetriever

# from langchain_core.prompts import PromptTemplate


class ResponseModel:

# This function takes message and we responed with LLM generated response 
    @classmethod
    def response_model (cls,message, llm_model= 'llama3.2'):
        model= OllamaLLM(model=llm_model)
        retriver= DocumentRetriever()

        # print('This is the message in the response model', message)

        print('Yes triggered by the slack_shared message')

        relevant_chunk= retriver.search(message)

        # print('This is the relevant chunk', relevant_chunk)
        relevant_chunks=relevant_chunk['data']['Get']['Documentation'][0]['content']

        print('this is the relevant chunk received', relevant_chunks)

        # Using promptTemplate modules from the langchain 
        # prompt_template="This is a Retrieval-Augmented Generation (RAG) system. Here is the user's query: {query}. Below is the relevant information retrieved: {chunk} also give the retrived chunk in relevant part and also rate the retrived chunk bassed on the query  and if retrived content has example liek html or code always add that in response."
        prompt_template= 'This is the user query -> {query} detect the code and response base on the chunk recieved and the user query'
        formatted_prompt = prompt_template.format(query=relevant_chunks)

        return model.invoke(formatted_prompt)
    
    

    





    
    

