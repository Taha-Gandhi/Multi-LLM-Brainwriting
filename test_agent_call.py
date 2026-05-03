from src.llm_client import ask_model

response = ask_model(
    agent_name="Test Agent",
    model_id="openrouter/free",
    prompt="Generate one creative idea to reduce food waste among university students."
)

print(response)