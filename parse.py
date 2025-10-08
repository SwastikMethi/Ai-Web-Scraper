
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter

template = (
    "You are tasked with extracting specific information from the following text content:\n{dom_content}\n\n"
    "Follow these rules strictly:\n"
    "1. Extract only what matches: {parse_description}\n"
    "2. No explanations or extra text.\n"
    "3. If nothing matches, return an empty string ('').\n"
)

qa_template = (
    "You are a helpful assistant. You are given website content:\n\n"
    "{dom_content}\n\n"
    "Now answer this question about the site:\n{question}"
)

def embed_text(embedding_model, texts):
    texts = [t.strip() for t in texts if t and isinstance(t, str) and t.strip()]
    print(f"Embedding {len(texts)} chunks...")

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunked_texts = []
    for t in texts:
        chunked_texts.extend(splitter.split_text(t))
    
    print(f"Total chunks after splitting: {len(chunked_texts)}")

    try:
        vector_store = FAISS.from_texts(chunked_texts, embedding_model)
        print("Embedding successful.")
        return vector_store
    except Exception as e:
        print("❌ Embedding failed:", e)
        raise

def context_search(vector_store, query, k=3):
    docs = vector_store.similarity_search(query, k=k)
    return [doc.page_content for doc in docs]

def parse_with_ollama(model, created_chunks, description):
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model

    results = []
    print(f"Parsing with description: {description}")
    for chunk in created_chunks:
        response = chain.invoke({
            "dom_content": chunk,
            "parse_description": description
        })
        results.append(response)

    return "\n".join([r for r in results if r.strip()])

def ask_about_site(model, vector_store, question: str) -> str:
    print(f"Searching for context for question: {question}")
    relevant_docs = context_search(vector_store, question)
    print("Relevant documents retrieved.")
    context = "\n\n".join(relevant_docs)

    prompt = ChatPromptTemplate.from_template(qa_template)
    chain = prompt | model

    response = chain.invoke({
        "dom_content": context,
        "question": question
    })
    return response
