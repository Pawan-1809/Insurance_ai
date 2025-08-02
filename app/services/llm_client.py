# LLM (OpenAI GPT-4) client
import openai
from app.core.config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

# TODO: Add prompt templates, rationale extraction, and error handling

def ask_llm(prompt: str, model: str = "gpt-4") -> str:
    response = openai.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=512
    )
    content = None
    if response.choices and response.choices[0].message and response.choices[0].message.content:
        content = response.choices[0].message.content
    return content.strip() if content else ""
