import os
import time

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv():
        return None

try:
    from openai import OpenAI, RateLimitError, APIError
except ImportError:
    OpenAI = None

    class RateLimitError(Exception):
        pass

    class APIError(Exception):
        pass

load_dotenv()

client = None

FALLBACK_MODELS = [
    "openrouter/free",
    "openai/gpt-oss-120b:free",
    "qwen/qwen3-coder:free",
    "nvidia/nemotron-3-super:free",
    "inclusionai/ring-2.6-1t:free",
    "poolside/laguna-m1:free",
]


def get_client():
    global client

    if client is None:
        if OpenAI is None:
            raise ImportError(
                "The openai package is not installed. Run `pip install -r requirements.txt` first."
            )

        current_api_key = os.getenv("OPENROUTER_API_KEY")

        if not current_api_key:
            raise ValueError(
                "OPENROUTER_API_KEY not found. Please add it to your .env file."
            )

        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=current_api_key,
        )

    return client


def ask_model(agent_name, model_id, prompt, system_prompt=None, temperature=0.7, max_retries=1):
    """
    Sends a prompt to OpenRouter.
    If one free model is rate-limited, it retries and then falls back.
    """

    if system_prompt is None:
        system_prompt = (
            f"You are {agent_name}, an independent AI agent in a multi-agent "
            "brainwriting system. Be logical, clear, concise, and respond only in English."
        )

    models_to_try = [model_id] + [m for m in FALLBACK_MODELS if m != model_id]

    last_error = None
    openrouter_client = get_client()

    for current_model in models_to_try:
        for attempt in range(max_retries):
            try:
                response = openrouter_client.chat.completions.create(
                    model=current_model,
                    messages=[
                        {
                            "role": "system",
                            "content": system_prompt + "\nRespond only in English. Keep responses concise."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        },
                    ],
                    temperature=temperature,
                )

                return response.choices[0].message.content

            except RateLimitError as error:
                last_error = error
                wait_time = 3
                print(
                    f"\nRate limit on {current_model}. "
                    f"Retrying in {wait_time} seconds..."
                )
                time.sleep(wait_time)

            except APIError as error:
                last_error = error
                print(f"\nAPI error on {current_model}. Trying fallback model...")
                break

            except Exception as error:
                last_error = error
                print(f"\nError on {current_model}: {error}")
                break

    raise RuntimeError(f"All models failed. Last error: {last_error}")
