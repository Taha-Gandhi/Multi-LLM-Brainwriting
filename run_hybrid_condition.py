import os
from src.llm_client import ask_model
from src.agents import AGENTS

DESIGN_CHALLENGE = (
    "Design a solution that improves creative collaboration and idea selection "
    "in group brainwriting."
)

MAX_DEBATE_ROUNDS = 1
os.makedirs("outputs", exist_ok=True)


def read_human_ideas():
    path = "human_ideas_input.txt"

    if not os.path.exists(path):
        raise FileNotFoundError(
            "human_ideas_input.txt not found. Create it and paste the anonymous human ideas inside."
        )

    with open(path, "r", encoding="utf-8") as file:
        return file.read()


def format_dict(data):
    return "\n\n".join([f"{key}:\n{value}" for key, value in data.items()])


def assign_human_ideas_to_agents(human_ideas):
    print("\n========== STAGE 1: ASSIGN HUMAN IDEAS TO LLM AGENTS ==========")

    prompt = f"""
Design challenge:
{DESIGN_CHALLENGE}

Anonymous human-generated ideas:
{human_ideas}

Assign these human ideas fairly to the available LLM agents:
{', '.join(AGENTS.keys())}

Each agent should defend and improve one human idea, but they may also critique others later.

Return in this format:
Agent Name:
Assigned Human Idea:

IMPORTANT OUTPUT RULES:
- Respond only in English.
- Do not use Markdown tables.
- Do not use long bullet lists.
- Keep your answer short and readable for human evaluators.


"""

    assignment = ask_model(
        agent_name="Assignment Moderator",
        model_id="openrouter/free",
        prompt=prompt,
        temperature=0.3,
    )

    print(assignment)
    return assignment


def debate_human_ideas(human_ideas, assignment):
    print("\n========== STAGE 2: LLM DEBATE ON HUMAN IDEAS ==========")

    debate_rounds = []

    for round_number in range(1, MAX_DEBATE_ROUNDS + 1):
        current_responses = {}

        previous_debate = ""
        for past_round in debate_rounds:
            previous_debate += f"\nROUND {past_round['round']}:\n"
            previous_debate += format_dict(past_round["responses"])

        for agent_name, agent_info in AGENTS.items():
            print(f"{agent_name} debating human ideas...")

            prompt = f"""
You are participating in Round {round_number} of the HYBRID condition.

In this condition, humans generated the original ideas anonymously.
Your job is to debate, defend, critique, and improve these human ideas.

Design challenge:
{DESIGN_CHALLENGE}

Anonymous human ideas:
{human_ideas}

Agent assignment:
{assignment}

Previous debate:
{previous_debate if previous_debate else "No previous debate yet."}

Your task:
1. Defend the strongest parts of the human idea assigned to you.
2. Critique one weakness in another idea.
3. Suggest how the human ideas can be merged into a stronger collaborative solution.
4. Say which direction should become the final base idea.

IMPORTANT OUTPUT RULES:
- Respond only in English.
- Do not use Markdown tables.
- Do not use long bullet lists.
- Keep your answer short and readable for human evaluators.

Style:
- Respond only in English.
- Keep it under 80 words.
- Use 1 short paragraph only.
- Be lively, direct, and human-readable.
- You can disagree strongly, but keep it about the idea.
- No long introductions.
- No Markdown headings.

"""

            current_responses[agent_name] = ask_model(
                agent_name=agent_name,
                model_id=agent_info["model"],
                prompt=prompt,
                system_prompt=agent_info["system_prompt"],
                temperature=0.8,
            )

        debate_rounds.append({"round": round_number, "responses": current_responses})

    return debate_rounds


def create_hybrid_candidates(human_ideas, debate_rounds):
    print("\n========== STAGE 3: CREATE HYBRID CANDIDATE IDEAS ==========")

    prompt = f"""
You are the Hybrid Collaborative Idea Builder.

Design challenge:
{DESIGN_CHALLENGE}

Human-generated ideas:
{human_ideas}

LLM debate transcript:
{debate_rounds}

Create THREE improved hybrid candidate ideas.
These should preserve the best human ideas while improving clarity, feasibility, and implementation.

Keep each candidate under 80 words.

Return exactly in this format:

Candidate 1:
Title:
Concept:

Candidate 2:
Title:
Concept:

Candidate 3:
Title:
Concept:

IMPORTANT OUTPUT RULES:
- Respond only in English.
- Do not use Markdown tables.
- Do not use long bullet lists.
- Keep your answer short and readable for human evaluators.
- Keep each candidate under 70 words.
- Respond only in English.
- Do not use Markdown tables.
"""

    return ask_model(
        agent_name="Hybrid Idea Builder",
        model_id="openrouter/free",
        prompt=prompt,
        temperature=0.55,
    )


def vote_hybrid_candidates(candidate_ideas):
    print("\n========== STAGE 4: LLM VOTING ON HYBRID CANDIDATES ==========")

    votes = {}

    for agent_name, agent_info in AGENTS.items():
        print(f"{agent_name} voting on hybrid candidates...")

        prompt = f"""
You are voting on hybrid candidate ideas.

Design challenge:
{DESIGN_CHALLENGE}

Candidate ideas:
{candidate_ideas}

Score each candidate from 1 to 10 on:
- Relevance
- Insightfulness
- Innovation

Keep your response under 80 words.

Return in this format:
Candidate 1 Score:
Candidate 2 Score:
Candidate 3 Score:

Chosen Candidate:
Reason:

IMPORTANT OUTPUT RULES:
- Respond only in English.
- Do not use Markdown tables.
- Do not use long bullet lists.
- Keep your answer short and readable for human evaluators.
"""

        votes[agent_name] = ask_model(
            agent_name=agent_name,
            model_id=agent_info["model"],
            prompt=prompt,
            system_prompt=agent_info["system_prompt"],
            temperature=0.35,
        )

    return votes


def synthesize_final_hybrid_idea(human_ideas, assignment, debate_rounds, candidate_ideas, votes):
    print("\n========== STAGE 5: FINAL HYBRID SYNTHESIS ==========")

    prompt = f"""
You are the Final Moderator for the HYBRID human-idea + LLM-debate condition.

Design challenge:
{DESIGN_CHALLENGE}

Human-generated ideas:
{human_ideas}

Agent assignment:
{assignment}

LLM debate:
{debate_rounds}

Hybrid candidate ideas:
{candidate_ideas}

Votes:
{format_dict(votes)}

Produce ONE final hybrid collaborative idea.

Keep it under 100 words.

Return in this format:

Final Idea Title:
Final Idea Summary:
How It Works:
Why This Idea Was Selected:

IMPORTANT OUTPUT RULES:
- Respond only in English.
- Do not use Markdown tables.
- Do not use long bullet lists.
- Keep your answer short and readable for human evaluators.

"""

    return ask_model(
        agent_name="Final Hybrid Moderator",
        model_id="openrouter/free",
        prompt=prompt,
        temperature=0.4,
    )


def save_html_transcript(human_ideas, assignment, debate_rounds, candidate_ideas, votes, final_idea):
    path = "outputs/hybrid_debate_transcript.html"

    agent_colors = {
        "GPT_Agent": "#2563eb",
        "Creative_Agent": "#9333ea",
        "Practical_Agent": "#059669",
        "Critical_Agent": "#dc2626",
        "Ethics_Agent": "#ea580c",
    }

    def escape_html(text):
        return (
            str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("\n", "<br>")
        )

    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Hybrid Debate Transcript</title>
<style>
body {{
  font-family: Inter, Arial, sans-serif;
  background: #f8fafc;
  color: #0f172a;
  margin: 0;
  padding: 40px;
}}
.container {{
  max-width: 1000px;
  margin: auto;
}}
.header, .stage {{
  background: white;
  border-radius: 26px;
  padding: 26px;
  margin-bottom: 22px;
  box-shadow: 0 12px 35px rgba(15,23,42,0.07);
}}
h1 {{
  margin: 0;
  font-size: 34px;
}}
.sub {{
  color: #64748b;
  line-height: 1.6;
}}
.card {{
  background: white;
  border: 1px solid #e2e8f0;
  border-left: 6px solid #0f172a;
  border-radius: 18px;
  padding: 16px;
  margin: 12px 0;
}}
.agent {{
  font-weight: 800;
  margin-bottom: 8px;
}}
.final {{
  background: #ecfdf5;
  border: 1px solid #bbf7d0;
}}
</style>
</head>
<body>
<div class="container">
<div class="header">
<h1>Hybrid Human Ideas + LLM Debate</h1>
<p class="sub"><strong>Design Challenge:</strong><br>{escape_html(DESIGN_CHALLENGE)}</p>
</div>

<div class="stage">
<h2>Stage 1: Anonymous Human Ideas</h2>
<p>{escape_html(human_ideas)}</p>
</div>

<div class="stage">
<h2>Stage 2: Assignment</h2>
<p>{escape_html(assignment)}</p>
</div>

<div class="stage">
<h2>Stage 3: Short LLM Debate</h2>
"""

    for round_data in debate_rounds:
        html += f"<h3>Round {round_data['round']}</h3>"
        for agent_name, response in round_data["responses"].items():
            color = agent_colors.get(agent_name, "#0f172a")
            html += f"""
<div class="card" style="border-left-color:{color};">
<div class="agent" style="color:{color};">{escape_html(agent_name)}</div>
<div>{escape_html(response)}</div>
</div>
"""

    html += f"""
</div>

<div class="stage">
<h2>Stage 4: Hybrid Candidate Ideas</h2>
<p>{escape_html(candidate_ideas)}</p>
</div>

<div class="stage">
<h2>Stage 5: Votes</h2>
<p>{escape_html(format_dict(votes))}</p>
</div>

<div class="stage final">
<h2>Final Hybrid Collaborative Idea</h2>
<p>{escape_html(final_idea)}</p>
</div>

</div>
</body>
</html>
"""

    with open(path, "w", encoding="utf-8") as file:
        file.write(html)

    print(f"Saved HTML transcript to {path}")


def save_text_output(human_ideas, assignment, debate_rounds, candidate_ideas, votes, final_idea):
    path = "outputs/hybrid_condition_output.txt"

    with open(path, "w", encoding="utf-8") as file:
        file.write("HYBRID HUMAN IDEAS + LLM DEBATE CONDITION\n")
        file.write("=" * 80 + "\n\n")

        file.write("DESIGN CHALLENGE\n")
        file.write(DESIGN_CHALLENGE + "\n\n")

        file.write("HUMAN IDEAS\n")
        file.write("=" * 80 + "\n")
        file.write(human_ideas + "\n\n")

        file.write("ASSIGNMENT\n")
        file.write("=" * 80 + "\n")
        file.write(assignment + "\n\n")

        file.write("DEBATE\n")
        file.write("=" * 80 + "\n")
        for round_data in debate_rounds:
            file.write(f"\nROUND {round_data['round']}\n")
            file.write(format_dict(round_data["responses"]))

        file.write("\n\nHYBRID CANDIDATES\n")
        file.write("=" * 80 + "\n")
        file.write(candidate_ideas + "\n\n")

        file.write("VOTES\n")
        file.write("=" * 80 + "\n")
        file.write(format_dict(votes) + "\n\n")

        file.write("FINAL HYBRID IDEA\n")
        file.write("=" * 80 + "\n")
        file.write(final_idea)

    print(f"Saved text output to {path}")


def main():
    human_ideas = read_human_ideas()
    assignment = assign_human_ideas_to_agents(human_ideas)
    debate_rounds = debate_human_ideas(human_ideas, assignment)
    candidate_ideas = create_hybrid_candidates(human_ideas, debate_rounds)
    votes = vote_hybrid_candidates(candidate_ideas)
    final_idea = synthesize_final_hybrid_idea(
        human_ideas, assignment, debate_rounds, candidate_ideas, votes
    )

    save_text_output(human_ideas, assignment, debate_rounds, candidate_ideas, votes, final_idea)
    save_html_transcript(human_ideas, assignment, debate_rounds, candidate_ideas, votes, final_idea)

    print("\n========== FINAL HYBRID IDEA ==========")
    print(final_idea)


if __name__ == "__main__":
    main()