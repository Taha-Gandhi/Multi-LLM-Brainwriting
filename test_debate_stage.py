import os
from src.llm_client import ask_model
from src.agents import AGENTS

challenge = "Design a real-world implementable solution to reduce food waste among university students."

idea_prompt = f"""
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

print("\n========== STAGE 1: INDEPENDENT IDEA GENERATION ==========")

for agent_name, agent_info in AGENTS.items():
    print(f"\nGenerating idea from {agent_name}...")

    ideas[agent_name] = ask_model(
        agent_name=agent_name,
        model_id=agent_info["model"],
        prompt=idea_prompt,
        system_prompt=agent_info["system_prompt"],
        temperature=0.8
    )

all_ideas_text = "\n\n".join(
    [f"{agent_name}'s idea:\n{idea}" for agent_name, idea in ideas.items()]
)

print("\n========== STAGE 2: MULTI-ROUND DEBATE ==========")

MAX_DEBATE_ROUNDS = 2
MIN_DEBATE_ROUNDS = 2

debate_rounds = []

for round_number in range(1, MAX_DEBATE_ROUNDS + 1):
    print(f"\n----- Debate Round {round_number} -----")

    previous_debate_text = ""

    for past_round in debate_rounds:
        previous_debate_text += f"\n\nROUND {past_round['round']}:\n"
        for speaker, response in past_round["responses"].items():
            previous_debate_text += f"\n{speaker}:\n{response}\n"

    current_round_responses = {}

    for agent_name, agent_info in AGENTS.items():
        print(f"\n{agent_name} is responding in round {round_number}...")

        if round_number == 1:
            round_instruction = (
                "This is the opening debate round. Defend your own idea strongly, "
                "point out weaknesses in competing ideas, and make a clear case for why your idea deserves to be the base idea."
            )
        elif round_number < MAX_DEBATE_ROUNDS:
            round_instruction = (
                "This is a response round. React directly to previous arguments, challenge weak claims, "
                "admit when another agent made a good point, and start moving toward a stronger merged solution."
            )
        else:
            round_instruction = (
                "This is the final debate round. Stop circling. Push the team toward a decision, "
                "choose the best base idea, and explain what must be merged into the final solution."
            )

        if {round_number} == 1:
                convergence_rule = "For Round 1, you should usually end with READY_TO_CONVERGE: NO because this is only the opening argument."
        else:
                convergence_rule = "You may end with READY_TO_CONVERGE: YES only if you believe the team has a clear logical direction."
            

        debate_prompt = f"""
            You are participating in Round {round_number} of an autonomous multi-agent debate.
            Round-specific instruction:
            {round_instruction}

            This is not a dry academic panel. You are debating like a real creative team:
            sharp, opinionated, expressive, witty, and sometimes mildly sarcastic.

            Design challenge:
            {challenge}

            Original generated ideas:
            {all_ideas_text}

            Previous debate transcript:
            {previous_debate_text if previous_debate_text else "No previous debate yet. This is the first round."}

            Convergence rule:
            {convergence_rule}
                
            Your task for this round:
            1. State your current position clearly.
            2. Defend your original idea if you still believe in it.
            3. If another agent's idea is weak, unrealistic, boring, expensive, or user-unfriendly, call it out directly.
            4. Respond directly to at least one other agent by name if previous debate exists.
            5. Use light humor, playful sarcasm, or a witty challenge when appropriate.
            6. Identify which idea should become the base idea and explain why.
            7. Suggest how the strongest parts can be merged into one final collaborative idea.
            8. You are allowed to change your mind if another agent gives a stronger argument.
            9. End with exactly one of these lines:
            READY_TO_CONVERGE: YES
            or
            READY_TO_CONVERGE: NO


            Debate style rules:
            - Do not say READY_TO_CONVERGE: YES in Round 1 unless the strongest base idea is extremely obvious.
            - Keep your response between 50 and 200 words.
            - Sound like a smart human teammate in a lively meeting.
            - Be fun and interesting to read.
            - Be confident, not robotic.
            - You may disagree strongly, but keep the disagreement about the idea, not the person.
            - Light roasting is allowed, but it must be tied to logical critique.
            - Do not use hate speech, slurs, personal abuse, or pointless insults.
            - Do not be overly polite if the idea has real weaknesses.
            - Avoid repeating your previous arguments unless you are adding a new point.

            Good example of tone:
            "Creative_Agent, I love the imagination, but this idea is dangerously close to becoming a glitter-covered logistics nightmare. Students need something they can use in 10 seconds, not a mini festival every time there is leftover pasta."

            Bad example of tone:
            "I respectfully acknowledge your perspective and agree that all ideas have merit."

            Write your response as a lively debate contribution.
        """

        response = ask_model(
            agent_name=agent_name,
            model_id=agent_info["model"],
            prompt=debate_prompt,
            system_prompt=agent_info["system_prompt"],
            temperature=0.95
        )

        current_round_responses[agent_name] = response

    debate_rounds.append({
        "round": round_number,
        "responses": current_round_responses
    })

    yes_count = sum(
        1 for response in current_round_responses.values()
        if "READY_TO_CONVERGE: YES" in response.upper()
    )

    if round_number >= MIN_DEBATE_ROUNDS and yes_count >= 2:
        print("\nConsensus signal reached. Moving to convergence stage.")
        break

print("\n\n========== FULL DEBATE TRANSCRIPT ==========")

for debate_round in debate_rounds:
    print(f"\n\nROUND {debate_round['round']}")
    print("=" * 60)

    for agent_name, response in debate_round["responses"].items():
        print("\n" + agent_name)
        print("-" * 60)
        print(response)

os.makedirs("outputs", exist_ok=True)

with open("outputs/debate_transcript.txt", "w", encoding="utf-8") as file:
    file.write("AUTONOMOUS MULTI-AGENT BRAINWRITING DEBATE TRANSCRIPT\n")
    file.write("=" * 70 + "\n\n")

    file.write("DESIGN CHALLENGE:\n")
    file.write(challenge + "\n\n")

    file.write("GENERATED IDEAS\n")
    file.write("=" * 70 + "\n\n")

    for agent_name, idea in ideas.items():
        file.write(agent_name + "\n")
        file.write("-" * 60 + "\n")
        file.write(idea + "\n\n")

    file.write("\nMULTI-ROUND DEBATE RESPONSES\n")
    file.write("=" * 70 + "\n\n")

    for debate_round in debate_rounds:
        file.write(f"ROUND {debate_round['round']}\n")
        file.write("=" * 60 + "\n\n")

        for agent_name, response in debate_round["responses"].items():
            file.write(agent_name + "\n")
            file.write("-" * 60 + "\n")
            file.write(response + "\n\n")

print("\nDebate transcript saved to outputs/debate_transcript.txt")