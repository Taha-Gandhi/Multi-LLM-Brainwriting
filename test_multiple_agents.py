import os

from src.llm_client import ask_model
from src.agents import AGENTS

challenge = "Design a real-world implementable solution to reduce food waste among university students."

prompt = f"""
You are participating in an autonomous brainwriting task.

Design challenge:
{challenge}

Generate ONE original idea independently.

Return your answer in this format:
Idea Title:
Problem:
Target Users:
Main Concept:
Why It Is Useful:
Implementation Steps:
Risks:
"""

ideas = {}

for agent_name, agent_info in AGENTS.items():
    print(f"\nGenerating idea from {agent_name}...")
    
    ideas[agent_name] = ask_model(
            agent_name=agent_name,
            model_id=agent_info["model"],
            prompt=prompt,
            system_prompt=agent_info["system_prompt"],
            temperature=0.8
        )

print("\n\n========== GENERATED IDEAS ==========")

for agent_name, idea in ideas.items():
    print("\n" + "=" * 60)
    print(agent_name)
    print("=" * 60)
    print(idea)

os.makedirs("outputs", exist_ok=True)

with open("outputs/generated_ideas.txt", "w", encoding="utf-8") as file:
    file.write("GENERATED IDEAS\n")
    file.write("=" * 60 + "\n\n")

    for agent_name, idea in ideas.items():
        file.write(agent_name + "\n")
        file.write("=" * 60 + "\n")
        file.write(idea + "\n\n")

print("\nIdeas saved to outputs/generated_ideas.txt")