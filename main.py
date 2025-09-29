import streamlit as st
from scrape import scrape_website, extract_body_content, clean_body_content, split_cleaned_content, scrape_website_uc
from parse import parse_with_ollama, ask_about_site

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
            "2. Chat with an AI about the website content.")

# Initialize session state
if "dom_content" not in st.session_state:
    st.session_state.dom_content = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # stores tuples (user_msg, ai_msg)

# Main Title
st.title("🤖 AI-Powered Web Scraper")
st.markdown("Extract and query website content using **AI**.")

# Scraping Section
st.subheader("🔍 Step 1: Scrape Website")
if st.button("🚀 Scrape Website", use_container_width=True):
    if url:
        with st.spinner("Scraping website..."):
            result = scrape_website(url)
            content = extract_body_content(result)
            cleaned_content = clean_body_content(content)
            st.session_state.dom_content = cleaned_content

        print("Scraping completed✅")
        st.toast("Scraping complete!", icon="✅")
        with st.expander("📄 Website Content", expanded=False):
            st.text_area(f"Content for: {url}", cleaned_content, height=400)
    else:
        st.error("❌ Please enter a valid URL.")

# If scraped content exists
if st.session_state.dom_content:

    # Parsing Section
    st.subheader("📝 Step 2: Parse Website Content")
    parse_description = st.text_area(
        "🔑 Describe the information you want to extract",
        placeholder="e.g., Extract all email addresses from the site",
        key="parse_input"
    )

    if st.button("📌 Parse Content", use_container_width=True):
        if parse_description:
            with st.spinner("Parsing content..."):
                text_chunks = split_cleaned_content(st.session_state.dom_content)
                response = parse_with_ollama(text_chunks, parse_description)

            st.toast("✅ Parsing complete!", icon="✨")
            st.success("### Extracted Information")
            st.write(response)
        else:
            st.warning("⚠️ Please describe what you want to parse.")

    # Chatbot Section
    st.subheader("💬 Step 3: Chat with AI About Website")

    # Show chat history
    if st.session_state.chat_history:
        # st.markdown("### 🗨️ Chat History")
        for user_msg, ai_msg in st.session_state.chat_history:
            st.chat_message("user").write(user_msg)
            st.chat_message("assistant").write(ai_msg)

    chatbot_description = st.chat_input("💭 Ask anything about the scraped website...")
    if chatbot_description:
        with st.spinner("AI is thinking..."):
            response = ask_about_site(st.session_state.dom_content, chatbot_description)

        # Save to history
        st.session_state.chat_history.append((chatbot_description, response))

        # Display immediately
        st.chat_message("user").write(chatbot_description)
        st.chat_message("assistant").write(response)

# import streamlit as st
# from scrape import scrape_website, extract_body_content, clean_body_content, split_cleaned_content
# from parse import parse_with_ollama, ask_about_site
# st.title("AI Web Scraper")
# url = st.text_input("Enter Website URL", help="www.example.com")

# if st.button("Scrape Website"):
#     if url:
#         st.write("Scraping website")
#         result = scrape_website(url)
#         content = extract_body_content(result)
#         cleaned_content = clean_body_content(content)

#         st.session_state.dom_content = cleaned_content

#         with st.expander("Website Content"):
#             st.text_area(f"Content for: {url}",cleaned_content, height=400)

#     else:
#         st.error("Please enter url")

        
# if "dom_content" in st.session_state:

#     # Parsing section
#     parse_description = st.text_area("Describe what you want to parse?")
#     if st.button("Parse content"):
#         if parse_description:
#             with st.spinner("Parsing the content..."):
#                 text_chunks = split_cleaned_content(st.session_state.dom_content)
#                 response = parse_with_ollama(text_chunks, parse_description)
#             st.success("Parsed Successfully.")
#             st.write(response)
#         else:
#             st.warning("Please enter a description to parse.")

#     # Chatbot section
#     chatbot_description = st.text_area("Ask AI about the website")
#     if st.button("Ask AI about website"):
#         if chatbot_description:
#             with st.spinner("Getting AI response..."):
#                 response = ask_about_site(st.session_state.dom_content, chatbot_description)
#             st.success("Response received.")
#             st.write(response)
#         else:
#             st.warning("Please enter a question before asking AI.")
        
             



# import streamlit as st
# from scrape import scrape_website, extract_body_content, clean_body_content, split_cleaned_content
# from parse import parse_with_ollama, ask_about_site

# # Page config
# st.set_page_config(page_title="AI Web Scraper", page_icon="🤖", layout="wide")

# # Sidebar
# with st.sidebar:
#     st.title("⚙️ Controls")
#     url = st.text_input("🌐 Enter Website URL", placeholder="https://example.com")
#     st.caption("Provide a full valid URL including `https://`.")

#     st.divider()
#     st.markdown("### ℹ️ About")
#     st.info("This tool scrapes websites and lets you:\n"
#             "1. Parse specific details.\n"
#             "2. Chat with an AI about the website content.")

# # Main Title
# st.title("🤖 AI-Powered Web Scraper")
# st.markdown("Extract and query website content using **AI**.")

# # Scraping Section
# st.subheader("🔍 Step 1: Scrape Website")
# col1, col2 = st.columns([3,1])

# with col1:
#     if st.button("🚀 Scrape Website", use_container_width=True):
#         if url:
#             with st.spinner("Scraping website..."):
#                 result = scrape_website(url)
#                 content = extract_body_content(result)
#                 cleaned_content = clean_body_content(content)
#                 st.session_state.dom_content = cleaned_content

#             st.toast("✅ Scraping complete!", icon="✅")
#             with st.expander("📄 Website Content", expanded=False):
#                 st.text_area(f"Content for: {url}", cleaned_content, height=400)
#         else:
#             st.error("❌ Please enter a valid URL.")

# # If scraped content exists
# if "dom_content" in st.session_state:

#     # Parsing Section
#     st.subheader("📝 Step 2: Parse Website Content")
#     parse_description = st.text_area("🔑 Describe the information you want to extract", 
#                                      placeholder="e.g., Extract all email addresses from the site")

#     if st.button("📌 Parse Content", use_container_width=True):
#         if parse_description:
#             with st.spinner("Parsing content..."):
#                 text_chunks = split_cleaned_content(st.session_state.dom_content)
#                 response = parse_with_ollama(text_chunks, parse_description)

#             st.toast("✅ Parsing complete!", icon="✨")
#             st.success("### Extracted Information")
#             st.write(response)
#         else:
#             st.warning("⚠️ Please describe what you want to parse.")

#     # Chatbot Section
#     st.subheader("💬 Step 3: Chat with AI About Website")
#     chatbot_description = st.text_area("🤔 Ask anything about the scraped website",
#                                        placeholder="e.g., Summarize the website in 3 bullet points")

#     if st.button("💡 Ask AI", use_container_width=True):
#         if chatbot_description:
#             with st.spinner("AI is thinking..."):
#                 response = ask_about_site(st.session_state.dom_content, chatbot_description)

#             st.toast("✅ AI response ready!", icon="🤖")
            
#             # Display like chat bubble
#             st.markdown("#### 🤖 AI says:")
#             st.info(response)
#         else:
#             st.warning("⚠️ Please enter a question before asking AI.")




