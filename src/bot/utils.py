from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate


# This function takes message and we responed with LLM generated response 
def response_model (message, llm_model= 'llama3.2'):
    model= OllamaLLM(model=llm_model)

    # Using promptTemplate modules from the langchain 
    prompt_template=PromptTemplate.from_template("Answer this query as a specialist: {query}")

    formatted_prompt = prompt_template.format(query=message)

    return model.invoke(formatted_prompt)

    
    

