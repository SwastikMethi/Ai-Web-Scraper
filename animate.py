import time
from langchain_ollama import ChatOllama

def type_writer(text, container, speed=0.02):
    """Display AI response with a typing animation."""
    typed_text = ""
    for char in text:
        typed_text += char
        container.markdown(f"{typed_text}")
        time.sleep(speed)