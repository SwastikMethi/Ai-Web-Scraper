from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

template = (
    "You are tasked with extracting specific information from the following text content: {dom_content}. "
    "Please follow these instructions carefully: \n\n"
    "1. **Extract Information:** Only extract the information that directly matches the provided description: {parse_description}. "
    "2. **No Extra Content:** Do not include any additional text, comments, or explanations in your response. "
    "3. **Empty Response:** If no information matches the description, return an empty string ('')."
    "4. **Direct Data Only:** Your output should contain only the data that is explicitly requested, with no other text."
)

qa_template = (
    "You are a helpful assistant. You are given website content:\n\n"
    "{dom_content}\n\n"
    "Now answer the following question about this website:\n{question}"
)

model = OllamaLLM(model = "llama3.2:latest")

def parse_with_ollama(created_chunks, description):
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model

    results = []

    for chunk in enumerate(created_chunks):
        response = chain.invoke({
            "dom_content": chunk , "parse_description": description
        })

        results.append(response)
    
    return "\n".join(results)

def ask_about_site(scraped_content: str, question: str) -> str:
    prompt = ChatPromptTemplate.from_template(qa_template)
    chain = prompt | model

    response = chain.invoke({
        "dom_content": scraped_content,
        "question": question
    })
    return response


