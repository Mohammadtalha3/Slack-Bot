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

        print('this is the relevant chunk received', relevant_chunk)

        # Using promptTemplate modules from the langchain 
        # prompt_template="This is a Retrieval-Augmented Generation (RAG) system. Here is the user's query: {query}. Below is the relevant information retrieved: {chunk} also give the retrived chunk in relevant part and also rate the retrived chunk bassed on the query  and if retrived content has example liek html or code always add that in response."
        prompt_template= 'Summarize the retrived chunk if you detect code specially keep it in the response. Here is the chunk {query}'
        formatted_prompt = prompt_template.format(query=relevant_chunk)

        return model.invoke(formatted_prompt)
    

# data=ResponseModel()
# dt2=data.response_model(message='How to use templates in django?')

# print(dt2)
    

    





    
    

