# LLM (OpenAI GPT-4) client
import openai
import requests
from app.core.config import OPENAI_API_KEY, LLM_MODEL
import logging

logger = logging.getLogger(__name__)

def ask_llm(prompt: str, model: str = None) -> str:
    """
    Send a prompt to the LLM and get a response.
    
    Args:
        prompt: The prompt to send to the LLM
        model: The model to use (defaults to LLM_MODEL from config)
        
    Returns:
        The LLM response as a string
    """
    try:
        model = model or LLM_MODEL
        
        # Try OpenAI client first
        try:
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,  # Lower temperature for more deterministic responses
                max_tokens=512,   # Reduced max tokens for faster responses
                request_timeout=15  # Set timeout to avoid long waits
            )
            
            if response.choices and response.choices[0].message and response.choices[0].message.content:
                content = response.choices[0].message.content
                logger.info(f"Successfully generated LLM response using {model}")
                return content.strip()
            else:
                logger.warning("LLM response was empty")
                return "No response generated from LLM."
                
        except Exception as client_error:
            logger.warning(f"OpenAI client failed, trying direct HTTP: {client_error}")
            
            # Fallback to direct HTTP request
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,  # Lower temperature for more deterministic responses
                "max_tokens": 512    # Reduced max tokens for faster responses
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('choices') and result['choices'][0].get('message'):
                    content = result['choices'][0]['message']['content']
                    logger.info(f"Successfully generated LLM response using direct HTTP")
                    return content.strip()
                else:
                    logger.warning("LLM response was empty")
                    return "No response generated from LLM."
            else:
                logger.error(f"HTTP request failed: {response.status_code} - {response.text}")
                return f"Error: HTTP {response.status_code} - {response.text}"
            
    except Exception as e:
        logger.error(f"LLM request failed: {e}")
        return f"Error generating response: {str(e)}"
