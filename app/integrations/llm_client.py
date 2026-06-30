import httpx
from app.core.config import settings

class LLMClientError(Exception):
    pass

class LLMClient:
    """
    Cliente para comunicarse con la API de OpenRouter.
    Aísla a la aplicación de los detalles específicos del proveedor.
    """
    
    BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

    @staticmethod
    def generate_feedback(system_prompt: str, user_answer: str) -> tuple[str, str]:

        headers = {
            "Authorization": f"Bearer {settings.openrouter_api_key}",
            "HTTP-Referer": "http://localhost:8000", 
            "X-Title": settings.app_name             
        }

        payload = {
            "model": settings.openrouter_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Respuesta del estudiante: {user_answer}"}
            ]
        }

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    LLMClient.BASE_URL,
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                
                feedback = data["choices"][0]["message"]["content"]
                raw_response = response.text
                
                return feedback, raw_response
                
        except httpx.HTTPError as e:
            raise LLMClientError(f"Error communicating with LLM Provider: {str(e)}")
        except (KeyError, IndexError) as e:
            raise LLMClientError(f"Unexpected response format from LLM Provider: {str(e)}")