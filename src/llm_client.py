import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    raise ValueError("OPENROUTER_API_KEY not found. Please add it to your .env file.")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)


def ask_model(agent_name, model_id, prompt, system_prompt=None, temperature=0.7):
    """
    Sends a prompt to a selected OpenRouter model and returns the response text.

    agent_name: The name/persona of the agent
    model_id: The OpenRouter model ID
    prompt: The user prompt we want the model to answer
    system_prompt: Optional custom personality/instruction for the agent
    temperature: Controls creativity. Higher = more creative, lower = more focused.
    """

    if system_prompt is None:
        system_prompt = (
            f"You are {agent_name}, an independent AI agent in a multi-agent "
            "brainwriting system. Be logical, clear, and concise."
        )

    response = client.chat.completions.create(
        model=model_id,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=temperature,
    )

    return response.choices[0].message.content