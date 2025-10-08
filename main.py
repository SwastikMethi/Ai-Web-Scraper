import streamlit as st
from scrape import split_cleaned_content, crawl_website
from parse import embed_text, parse_with_ollama, ask_about_site
from animate import type_writer
import sys
import asyncio
from langchain_community.embeddings import OllamaEmbeddings
import time
import config
from langchain_ollama import OllamaLLM, ChatOllama

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Page config
st.set_page_config(page_title="AI Web Scraper", page_icon="🤖", layout="wide")

# Sidebar
with st.sidebar:
    st.title("⚙️ Controls")
    url = st.text_input("🌐 Enter Website URL", placeholder="https://example.com")
    st.caption("Provide a full valid URL including `https://`.")

    st.divider()
    st.markdown("### ℹ️ About")
    st.info("This tool scrapes websites and lets you:\n"
            "1. Parse specific details.\n"
            "2. Chat with an AI about the website content.\n"
            "3. Optionally save embeddings to a FAISS vector store for reuse.\n"
            "4. Developed by Swastik Methi.")


# Initialize session state
if "dom_content" not in st.session_state:
    st.session_state.dom_content = None
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # stores tuples (user_msg, ai_msg)

# Main Title
st.title("🤖 AI-Powered Web Scraper")
st.markdown("Extract and query website content using **AI**.")

# Scraping Section
st.subheader("🔍 Step 1: Scrape Website")
max_pages = st.slider("📄 Max Pages to Crawl", min_value=2, max_value=100, value=20)

embedding_model = OllamaEmbeddings(model=config.embedding_model)
model = OllamaLLM(model=config.model)

if st.button("🚀 Scrape Website", use_container_width=True):
    if url:
        progress = st.empty()
        progress.info(f"🌐 Starting crawl for: {url}")
        all_text = ""

        for page_no, current_url, cleaned_text in crawl_website(url, headless=True, max_pages=max_pages):
            if page_no == "done":
                progress.success(current_url)
                all_text = cleaned_text
                break
            else:
                progress.info(f"🕸️ Crawling page {page_no}: {current_url}")

        # Save scraped content
        st.session_state.dom_content = all_text
        print("Scraping completed ✅")
        st.toast("Scraping complete!", icon="✅")

        with st.expander("📄 Website Content", expanded=False):
            st.text_area(f"Content for: {url}", all_text, height=400)

    else:
        st.error("❌ Please enter a valid URL.")

# Save Embeddings Button
if st.session_state.dom_content:
    st.subheader("💾 Step 2: Save Website Embeddings")

    if st.button("💾 Save Embeddings to Vector Store", use_container_width=True):
        with st.spinner("Creating embeddings and saving to Vector Store..."):
            chunks = split_cleaned_content(st.session_state.dom_content)
            # chunks = [c for c in chunks if len(c.strip()) > 50]
            vector_store = embed_text(embedding_model, chunks)
            st.session_state.vector_store = vector_store
            vector_store.save_local("vector_store_index")

        st.toast("✅ Embeddings saved locally!", icon="💾")
        st.success("Vector store successfully created and saved!")

# Parsing Section
if st.session_state.dom_content:
    st.subheader("📝 Step 3: Parse Website Content")
    parse_description = st.text_area(
        "🔑 Describe the information you want to extract",
        placeholder="e.g., Extract all email addresses from the site",
        key="parse_input"
    )

    if st.button("📌 Parse Content", use_container_width=True):
        if parse_description:
            with st.spinner("Parsing content..."):
                text_chunks = split_cleaned_content(st.session_state.dom_content)
                response = parse_with_ollama(model, text_chunks, parse_description)

            st.toast("✅ Parsing complete!", icon="✨")
            st.success("### Extracted Information")
            st.markdown(response)
        else:
            st.warning("⚠️ Please describe what you want to parse.")

# Chatbot Section
if st.session_state.vector_store:
    st.subheader("💬 Step 4: Chat with AI About Website")

    # Show chat history
    if st.session_state.chat_history:
        for user_msg, ai_msg in st.session_state.chat_history:
            st.chat_message("user").write(user_msg)
            st.chat_message("assistant").write(ai_msg)

    chatbot_description = st.chat_input("💭 Ask anything about the scraped website...")
    
    if chatbot_description:
        st.chat_message("user").write(chatbot_description)
        with st.spinner("AI is thinking..."):
            response = ask_about_site(model, st.session_state.vector_store, chatbot_description)

        ai_message_placeholder = st.empty()
        type_writer(response, ai_message_placeholder, speed=0.02)
        st.session_state.chat_history.append((chatbot_description, response))
else:
    st.info("💡 Scrape and save embeddings first to enable chat.")
