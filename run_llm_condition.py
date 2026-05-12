import os
from src.llm_client import ask_model
from src.agents import AGENTS

DESIGN_CHALLENGE = (
    "Design a solution that improves creative collaboration and idea selection "
    "in group brainwriting."
)

MAX_DEBATE_ROUNDS = 2
os.makedirs("outputs", exist_ok=True)


def format_dict(data):
    return "\n\n".join([f"{key}:\n{value}" for key, value in data.items()])


def generate_ideas():
    print("\n========== STAGE 1: LLM IDEA GENERATION ==========")

    ideas = {}

    prompt = f"""
Design challenge:
{DESIGN_CHALLENGE}

Generate ONE original idea independently.

Return in this format:
Idea Title:
Problem:
Why It Is Useful:

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

    for agent_name, agent_info in AGENTS.items():
        print(f"\nGenerating idea from {agent_name}...")

        ideas[agent_name] = ask_model(
            agent_name=agent_name,
            model_id=agent_info["model"],
            prompt=prompt,
            system_prompt=agent_info["system_prompt"],
            temperature=0.8,
        )

    return ideas


def debate_original_ideas(ideas):
    print("\n========== STAGE 2: LLM DEBATE ==========")

    debate_rounds = []
    ideas_text = format_dict(ideas)

    for round_number in range(1, MAX_DEBATE_ROUNDS + 1):
        print(f"\n----- Debate Round {round_number} -----")

        previous_debate = ""

        for past_round in debate_rounds:
            previous_debate += f"\nROUND {past_round['round']}:\n"
            previous_debate += format_dict(past_round["responses"])

        current_responses = {}

        for agent_name, agent_info in AGENTS.items():
            print(f"{agent_name} debating...")

            prompt = f"""
You are participating in Round {round_number} of a multi-LLM debate.

Design challenge:
{DESIGN_CHALLENGE}

Original ideas:
{ideas_text}

Previous debate:
{previous_debate if previous_debate else "No previous debate yet."}

Your task:
1. Defend or revise your position.
2. Critique at least one weak idea.
3. Praise one useful element from another idea.
4. Say which idea should become the base idea.
5. Suggest how ideas can be merged.

IMPORTANT:
Your response will be shown to human evaluators. Keep it clean, short, and readable.

IMPORTANT OUTPUT RULES:
- Respond only in English.
- Do not use Markdown tables.
- Do not use long bullet lists.
- Keep your answer short and readable for human evaluators.

Style:
- Respond only in English.
- Keep it under 80 words.
- Use one short paragraph only.
- Be lively, direct, and human-readable.
- You can disagree strongly, but keep it about the idea.
- No Markdown headings.
- No tables.
- No long introductions.
"""

            current_responses[agent_name] = ask_model(
                agent_name=agent_name,
                model_id=agent_info["model"],
                prompt=prompt,
                system_prompt=agent_info["system_prompt"],
                temperature=0.85,
            )

        debate_rounds.append(
            {
                "round": round_number,
                "responses": current_responses,
            }
        )

    return debate_rounds


def create_merged_candidates(ideas, debate_rounds):
    print("\n========== STAGE 3: CREATE MERGED CANDIDATE IDEAS ==========")

    prompt = f"""
You are the Collaborative Idea Builder.
Keep your voting response under 80 words.

Design challenge:
{DESIGN_CHALLENGE}

Original ideas:
{format_dict(ideas)}

Debate transcript:
{debate_rounds}

Create THREE improved collaborative candidate ideas based on the strongest points from the debate.

Return exactly in this format:

Candidate 1:
Title:
Concept:
Merged Elements:

Candidate 2:
Title:
Concept:
Merged Elements:

Candidate 3:
Title:
Concept:
Merged Elements:

IMPORTANT OUTPUT RULES:
- Respond only in English.
- Do not use Markdown tables.
- Do not use long bullet lists.
- Keep your answer short and readable for human evaluators.

"""

    return ask_model(
        agent_name="Collaborative Idea Builder",
        model_id="openrouter/free",
        prompt=prompt,
        temperature=0.55,
    )


def vote_on_candidates(candidate_ideas):
    print("\n========== STAGE 4: LLM VOTING ==========")

    votes = {}

    for agent_name, agent_info in AGENTS.items():
        print(f"{agent_name} voting...")

        prompt = f"""
You are voting on the final candidate ideas.
Keep each candidate under 80 words.

Design challenge:
{DESIGN_CHALLENGE}

Candidate ideas:
{candidate_ideas}

Score each candidate from 1 to 5 on:
- Relevance
- Insightfulness
- Innovation

Then choose ONE final candidate.

Return in this format:
Candidate 1 Score:
Candidate 2 Score:
Candidate 3 Score:

Chosen Candidate:
Reason:
Suggested Final Improvement:

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


def synthesize_final_idea(ideas, debate_rounds, candidate_ideas, votes):
    print("\n========== STAGE 5: FINAL MODERATOR SYNTHESIS ==========")

    prompt = f"""
You are the Final Moderator for the LLM-only brainwriting condition.
Keep te final idea under 100 words.
Design challenge:
{DESIGN_CHALLENGE}

Original ideas:
{format_dict(ideas)}

Debate transcript:
{debate_rounds}

Merged candidate ideas:
{candidate_ideas}

Votes:
{format_dict(votes)}

Produce ONE final collaborative idea.

Return in this format:

Final Idea Title:
Final Idea Summary:
Why This Idea Was Selected:

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

    return ask_model(
        agent_name="Final Moderator",
        model_id="openrouter/free",
        prompt=prompt,
        temperature=0.4,
    )


def save_output(ideas, debate_rounds, candidate_ideas, votes, final_idea):
    path = "outputs/llm_condition_output.txt"

    with open(path, "w", encoding="utf-8") as file:
        file.write("LLM-ONLY DEBATE BRAINWRITING CONDITION\n")
        file.write("=" * 80 + "\n\n")

        file.write("DESIGN CHALLENGE\n")
        file.write(DESIGN_CHALLENGE + "\n\n")

        file.write("STAGE 1: ORIGINAL LLM IDEAS\n")
        file.write("=" * 80 + "\n\n")
        file.write(format_dict(ideas))

        file.write("\n\nSTAGE 2: DEBATE TRANSCRIPT\n")
        file.write("=" * 80 + "\n\n")
        for round_data in debate_rounds:
            file.write(f"\nROUND {round_data['round']}\n")
            file.write("-" * 60 + "\n")
            file.write(format_dict(round_data["responses"]))
            file.write("\n\n")

        file.write("\nSTAGE 3: MERGED CANDIDATE IDEAS\n")
        file.write("=" * 80 + "\n\n")
        file.write(candidate_ideas)

        file.write("\n\nSTAGE 4: LLM VOTES\n")
        file.write("=" * 80 + "\n\n")
        file.write(format_dict(votes))

        file.write("\n\nSTAGE 5: FINAL LLM-ONLY IDEA\n")
        file.write("=" * 80 + "\n\n")
        file.write(final_idea)

    print(f"\nSaved to {path}")

def save_html_transcript(ideas, debate_rounds, candidate_ideas, votes, final_idea):
    path = "outputs/llm_debate_transcript.html"

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

    def clean_preview(text, max_chars=420):
        text = str(text)
        text = text.replace("**", "")
        text = text.replace("###", "")
        text = text.replace("##", "")
        text = text.replace("#", "")
        text = text.strip()

        if len(text) > max_chars:
            return text[:max_chars].strip() + "..."
        return text

    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>LLM Debate Transcript</title>
<style>
  * {{
    box-sizing: border-box;
  }}

  body {{
    font-family: Inter, Arial, sans-serif;
    background: #f8fafc;
    color: #0f172a;
    margin: 0;
    padding: 36px;
  }}

  .container {{
    max-width: 1080px;
    margin: auto;
  }}

  .header {{
    background: white;
    border-radius: 28px;
    padding: 32px;
    box-shadow: 0 14px 36px rgba(15,23,42,0.08);
    margin-bottom: 22px;
  }}

  .badge {{
    display: inline-block;
    background: #ecfdf5;
    color: #047857;
    border: 1px solid #bbf7d0;
    border-radius: 999px;
    padding: 7px 12px;
    font-size: 13px;
    font-weight: 800;
    margin-bottom: 14px;
  }}

  h1 {{
    margin: 0;
    font-size: 36px;
    letter-spacing: -1.2px;
  }}

  h2 {{
    margin: 0 0 16px;
    font-size: 23px;
    letter-spacing: -0.4px;
  }}

  h3 {{
    margin: 18px 0 10px;
  }}

  .sub {{
    color: #64748b;
    line-height: 1.65;
    margin-top: 12px;
  }}

  .stage {{
    background: white;
    border-radius: 26px;
    padding: 26px;
    margin-bottom: 22px;
    box-shadow: 0 10px 28px rgba(15,23,42,0.06);
  }}

  .grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 14px;
  }}

  .idea-card {{
    border: 1px solid #e2e8f0;
    border-radius: 20px;
    padding: 18px;
    background: #ffffff;
  }}

  .agent-name {{
    font-weight: 900;
    margin-bottom: 8px;
  }}

  .preview {{
    color: #475569;
    line-height: 1.55;
    font-size: 14px;
  }}

  .debate-card {{
    border-left: 6px solid #0f172a;
    background: #ffffff;
    border-radius: 18px;
    padding: 18px;
    margin: 12px 0;
    box-shadow: 0 6px 18px rgba(15,23,42,0.05);
  }}

  .round-label {{
    display: inline-block;
    padding: 8px 12px;
    border-radius: 999px;
    background: #0f172a;
    color: white;
    font-size: 13px;
    font-weight: 800;
    margin: 10px 0 8px;
  }}

  details {{
    margin-top: 12px;
    border-radius: 16px;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    padding: 12px 14px;
  }}

  summary {{
    cursor: pointer;
    font-weight: 800;
    color: #334155;
  }}

  .raw {{
    max-height: 260px;
    overflow-y: auto;
    color: #475569;
    line-height: 1.55;
    font-size: 14px;
    margin-top: 12px;
  }}

  .candidate-box {{
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 20px;
    padding: 18px;
    line-height: 1.6;
    color: #475569;
    max-height: 420px;
    overflow-y: auto;
  }}

  .final {{
    background: #ecfdf5;
    border: 1px solid #bbf7d0;
  }}

  .final p {{
    line-height: 1.7;
    color: #064e3b;
    font-size: 16px;
  }}

  .note {{
    margin-top: 8px;
    font-size: 13px;
    color: #64748b;
  }}

  @media (max-width: 900px) {{
    .grid {{
      grid-template-columns: 1fr;
    }}
    body {{
      padding: 18px;
    }}
  }}
</style>
</head>

<body>
<div class="container">

<div class="header">
  <div class="badge">LLM-Only Condition</div>
  <h1>Short Multi-Agent Debate Transcript</h1>
  <p class="sub"><strong>Design Challenge:</strong><br>{escape_html(DESIGN_CHALLENGE)}</p>
  <p class="sub">This version is cleaned for human readers. Long raw outputs are hidden inside dropdowns.</p>
</div>
"""

    html += """
<div class="stage">
  <h2>1. Original LLM Ideas</h2>
  <p class="note">Quick previews are shown below. Click each dropdown to inspect the full raw idea.</p>
  <div class="grid">
"""

    for agent_name, idea in ideas.items():
        color = agent_colors.get(agent_name, "#0f172a")
        html += f"""
    <div class="idea-card">
      <div class="agent-name" style="color:{color};">{escape_html(agent_name)}</div>
      <div class="preview">{escape_html(clean_preview(idea, 360))}</div>
      <details>
        <summary>View full idea</summary>
        <div class="raw">{escape_html(idea)}</div>
      </details>
    </div>
"""

    html += """
  </div>
</div>
"""

    html += """
<div class="stage">
  <h2>2. Short Debate</h2>
  <p class="note">Each agent gives a short argument, critique, or recommendation.</p>
"""

    for round_data in debate_rounds:
        html += f'<div class="round-label">Round {round_data["round"]}</div>'

        for agent_name, response in round_data["responses"].items():
            color = agent_colors.get(agent_name, "#0f172a")
            html += f"""
  <div class="debate-card" style="border-left-color:{color};">
    <div class="agent-name" style="color:{color};">{escape_html(agent_name)}</div>
    <div class="preview">{escape_html(clean_preview(response, 520))}</div>
  </div>
"""

    html += """
</div>
"""

    html += f"""
<div class="stage">
  <h2>3. Merged Candidate Ideas</h2>
  <p class="note">These are the improved ideas created after the debate.</p>
  <div class="candidate-box">{escape_html(candidate_ideas)}</div>
</div>
"""

    html += """
<div class="stage">
  <h2>4. Agent Votes</h2>
"""

    for agent_name, vote in votes.items():
        color = agent_colors.get(agent_name, "#0f172a")
        html += f"""
  <div class="debate-card" style="border-left-color:{color};">
    <div class="agent-name" style="color:{color};">{escape_html(agent_name)}</div>
    <div class="preview">{escape_html(clean_preview(vote, 500))}</div>
  </div>
"""

    html += """
</div>
"""

    html += f"""
<div class="stage final">
  <h2>5. Final LLM-Only Collaborative Idea</h2>
  <p>{escape_html(final_idea)}</p>
</div>

</div>
</body>
</html>
"""

    with open(path, "w", encoding="utf-8") as file:
        file.write(html)

    print(f"Saved clean HTML transcript to {path}")


def main():
    ideas = generate_ideas()
    debate_rounds = debate_original_ideas(ideas)
    candidate_ideas = create_merged_candidates(ideas, debate_rounds)
    votes = vote_on_candidates(candidate_ideas)
    final_idea = synthesize_final_idea(ideas, debate_rounds, candidate_ideas, votes)

    save_output(ideas, debate_rounds, candidate_ideas, votes, final_idea)
    save_html_transcript(ideas, debate_rounds, candidate_ideas, votes, final_idea)

    print("\n========== FINAL LLM-ONLY IDEA ==========")
    print(final_idea)


if __name__ == "__main__":
    main()