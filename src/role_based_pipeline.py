import argparse
import os
from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Dict, List

from src.agents import ROLE_AGENTS
from src.llm_client import ask_model


DEFAULT_DESIGN_CHALLENGE = (
    "Design a solution that improves creative collaboration and idea selection "
    "in group brainwriting."
)


@dataclass
class BrainwritingHyperparameters:
    design_challenge: str = DEFAULT_DESIGN_CHALLENGE
    iterations: int = 2
    max_ranked_ideas: int = 5
    idea_word_limit: int = 110
    evaluation_word_limit: int = 220
    strategy_word_limit: int = 140
    final_word_limit: int = 130
    idea_temperature: float = 0.8
    evaluation_temperature: float = 0.35
    strategy_temperature: float = 0.5
    final_temperature: float = 0.35
    initial_strategy_prompt: str = ""
    output_dir: str = "outputs"
    output_prefix: str = "llm_condition"
    final_agent_name: str = "Evaluation_Rigor_Agent"


@dataclass
class BrainwritingResult:
    seed_ideas: str
    seed_label: str
    idea_pool: Dict[str, str]
    generation_rounds: List[Dict]
    evaluation_rounds: List[Dict]
    strategy_rounds: List[Dict]
    final_idea: str


def build_arg_parser(default_output_prefix, description):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--challenge", default=DEFAULT_DESIGN_CHALLENGE)
    parser.add_argument("--iterations", type=int, default=2)
    parser.add_argument("--max-ranked-ideas", type=int, default=5)
    parser.add_argument("--idea-word-limit", type=int, default=110)
    parser.add_argument("--evaluation-word-limit", type=int, default=220)
    parser.add_argument("--strategy-word-limit", type=int, default=140)
    parser.add_argument("--final-word-limit", type=int, default=130)
    parser.add_argument("--idea-temperature", type=float, default=0.8)
    parser.add_argument("--evaluation-temperature", type=float, default=0.35)
    parser.add_argument("--strategy-temperature", type=float, default=0.5)
    parser.add_argument("--final-temperature", type=float, default=0.35)
    parser.add_argument("--initial-strategy-prompt", default="")
    parser.add_argument("--output-dir", default="outputs")
    parser.add_argument("--output-prefix", default=default_output_prefix)
    parser.add_argument("--final-agent-name", default="Evaluation_Rigor_Agent")
    return parser


def config_from_args(args):
    return BrainwritingHyperparameters(
        design_challenge=args.challenge,
        iterations=max(1, args.iterations),
        max_ranked_ideas=max(1, args.max_ranked_ideas),
        idea_word_limit=max(40, args.idea_word_limit),
        evaluation_word_limit=max(80, args.evaluation_word_limit),
        strategy_word_limit=max(60, args.strategy_word_limit),
        final_word_limit=max(60, args.final_word_limit),
        idea_temperature=args.idea_temperature,
        evaluation_temperature=args.evaluation_temperature,
        strategy_temperature=args.strategy_temperature,
        final_temperature=args.final_temperature,
        initial_strategy_prompt=args.initial_strategy_prompt,
        output_dir=args.output_dir,
        output_prefix=args.output_prefix,
        final_agent_name=args.final_agent_name,
    )


def format_dict(data):
    if not data:
        return "None yet."
    return "\n\n".join([f"{key}:\n{value}" for key, value in data.items()])


def format_rounds(rounds):
    if not rounds:
        return "None yet."

    chunks = []
    for round_data in rounds:
        chunks.append(f"ROUND {round_data['round']}")
        chunks.append(format_dict(round_data["responses"]))
        if "combined_prompt" in round_data:
            chunks.append("Combined strategy guidance:\n" + round_data["combined_prompt"])
    return "\n\n".join(chunks)


def call_agent(agent_name, agent_info, prompt, temperature):
    return ask_model(
        agent_name=agent_name,
        model_id=agent_info["model"],
        prompt=prompt,
        system_prompt=agent_info["system_prompt"],
        temperature=temperature,
    )


def build_generation_prompt(
    config,
    round_number,
    seed_ideas,
    seed_label,
    idea_pool,
    evaluation_rounds,
    strategy_guidance,
):
    current_ideas = format_dict(idea_pool)
    evaluations = format_rounds(evaluation_rounds)
    seed_block = seed_ideas.strip() if seed_ideas.strip() else "No seed ideas provided."

    if round_number == 1:
        round_instruction = (
            "Generate one strong candidate idea independently. If seed ideas are provided, "
            "you may revise, merge, or extend them, but the output must stand alone."
        )
    else:
        round_instruction = (
            "Generate one improved candidate for the next round. You may create a new idea "
            "or revise an existing idea, but you must respond to the evaluator feedback and "
            "strategy guidance instead of repeating earlier candidates."
        )

    return f"""
You are working in Stage 1: Idea Generation or Revision.

Design challenge:
{config.design_challenge}

Round:
{round_number}

Round instruction:
{round_instruction}

{seed_label}:
{seed_block}

Current candidate ideas:
{current_ideas}

Evaluation history:
{evaluations}

Strategy guidance for this generation round:
{strategy_guidance if strategy_guidance.strip() else "No extra strategy guidance yet."}

Return exactly in this format:
Action: NEW or REVISION
Idea Title:
Idea Summary:
What Changed or Why This Is New:

IMPORTANT OUTPUT RULES:
- Respond only in English.
- Keep the full response under {config.idea_word_limit} words.
- Do not use Markdown tables.
- Do not write a long introduction.
- Make the idea concrete enough that evaluators can judge it.
"""


def generate_or_revise_ideas(
    config,
    round_number,
    seed_ideas,
    seed_label,
    idea_pool,
    evaluation_rounds,
    strategy_guidance,
):
    print(f"\n========== STAGE 1: IDEA GENERATION ROUND {round_number} ==========")

    responses = {}
    prompt = build_generation_prompt(
        config,
        round_number,
        seed_ideas,
        seed_label,
        idea_pool,
        evaluation_rounds,
        strategy_guidance,
    )

    for agent_name, agent_info in ROLE_AGENTS["idea_generation"].items():
        print(f"{agent_name} generating or revising an idea...")
        response = call_agent(
            agent_name,
            agent_info,
            prompt,
            config.idea_temperature,
        )
        responses[agent_name] = response
        idea_pool[f"Round {round_number} / {agent_name}"] = response

    return {"round": round_number, "responses": responses}


def build_evaluation_prompt(config, round_number, idea_pool, generation_rounds):
    return f"""
You are working in Stage 2: Idea Evaluation, Analysis, and Ranking.

Design challenge:
{config.design_challenge}

Current candidate ideas:
{format_dict(idea_pool)}

Generation history:
{format_rounds(generation_rounds)}

Your task:
1. Evaluate every current candidate idea.
2. For each idea, identify one clear strength and one clear weakness.
3. Score each idea from 1 to 10 using relevance, usefulness, originality, feasibility, and clarity.
4. Rank the best {config.max_ranked_ideas} ideas from strongest to weakest.
5. Name the single best idea and explain why it should lead the final direction.

Return exactly in this format:
Evaluation Summary:
Per-Idea Analysis:
Top Ranking:
Best Idea:
Why It Is Best:
Risks or Fixes Needed:

IMPORTANT OUTPUT RULES:
- Respond only in English.
- Keep the full response under {config.evaluation_word_limit} words.
- Do not use Markdown tables.
- Be honest and do not favor any generator automatically.
"""


def evaluate_and_rank_ideas(config, round_number, idea_pool, generation_rounds):
    print(f"\n========== STAGE 2: EVALUATION ROUND {round_number} ==========")

    responses = {}
    prompt = build_evaluation_prompt(config, round_number, idea_pool, generation_rounds)

    for agent_name, agent_info in ROLE_AGENTS["idea_evaluation"].items():
        print(f"{agent_name} evaluating and ranking ideas...")
        responses[agent_name] = call_agent(
            agent_name,
            agent_info,
            prompt,
            config.evaluation_temperature,
        )

    return {"round": round_number, "responses": responses}


def build_strategy_prompt(config, round_number, idea_pool, evaluation_rounds):
    return f"""
You are working in Stage 3: Idea Generation Strategy Revision.

Design challenge:
{config.design_challenge}

Current candidate ideas:
{format_dict(idea_pool)}

Evaluation and ranking history:
{format_rounds(evaluation_rounds)}

Your task:
Create a control prompt that will be given to the Stage 1 idea generation agents in the next round.
The prompt should help them produce better ideas, not evaluate ideas and not write the final idea.

Focus on:
1. What the next generation agents should explore.
2. What weaknesses they must fix.
3. What constraints they must obey.
4. What repeated or low-value patterns they should avoid.

Return exactly in this format:
Next Generation Prompt:
Required Constraints:
Avoid:
Quality Bar:

IMPORTANT OUTPUT RULES:
- Respond only in English.
- Keep the full response under {config.strategy_word_limit} words.
- Do not use Markdown tables.
- Make the prompt directly reusable by the next generation agents.
"""


def revise_generation_strategy(config, round_number, idea_pool, evaluation_rounds):
    print(f"\n========== STAGE 3: STRATEGY REVISION ROUND {round_number} ==========")

    responses = {}
    prompt = build_strategy_prompt(config, round_number, idea_pool, evaluation_rounds)

    for agent_name, agent_info in ROLE_AGENTS["strategy_revision"].items():
        print(f"{agent_name} creating next-round strategy guidance...")
        responses[agent_name] = call_agent(
            agent_name,
            agent_info,
            prompt,
            config.strategy_temperature,
        )

    combined_prompt = combine_strategy_guidance(responses)
    return {
        "round": round_number,
        "responses": responses,
        "combined_prompt": combined_prompt,
    }


def combine_strategy_guidance(strategy_responses):
    return "\n\n".join(
        [
            f"{agent_name} guidance:\n{response}"
            for agent_name, response in strategy_responses.items()
        ]
    )


def build_final_prompt(config, result, final_agent_name):
    return f"""
You are {final_agent_name}, serving as the final convergence evaluator.

Design challenge:
{config.design_challenge}

Seed ideas or source material:
{result.seed_ideas if result.seed_ideas.strip() else "No seed ideas provided."}

All candidate ideas:
{format_dict(result.idea_pool)}

Evaluation and ranking history:
{format_rounds(result.evaluation_rounds)}

Strategy revision history:
{format_rounds(result.strategy_rounds)}

Produce ONE final collaborative idea.
You may select the highest-ranked idea or synthesize the strongest parts of the top-ranked ideas.
Do not add an unrelated new concept.

Return exactly in this format:
Final Idea Title:
Final Idea Summary:
Source Ideas Used:
Why This Idea Was Selected:
Remaining Risk:

IMPORTANT OUTPUT RULES:
- Respond only in English.
- Keep the full response under {config.final_word_limit} words.
- Do not use Markdown tables.
- Make the final idea clear enough for human evaluators who did not see the full transcript.
"""


def synthesize_final_idea(config, result):
    print("\n========== FINAL STAGE: SYNTHESIZE FINAL IDEA ==========")

    final_agents = ROLE_AGENTS["idea_evaluation"]
    agent_name = config.final_agent_name
    agent_info = final_agents.get(agent_name)

    if agent_info is None:
        agent_name, agent_info = next(iter(final_agents.items()))

    prompt = build_final_prompt(config, result, agent_name)
    return call_agent(
        agent_name,
        agent_info,
        prompt,
        config.final_temperature,
    )


def run_role_based_brainwriting(config, seed_ideas="", seed_label="Seed ideas"):
    os.makedirs(config.output_dir, exist_ok=True)

    idea_pool = {}
    if seed_ideas.strip():
        idea_pool[seed_label] = seed_ideas.strip()

    generation_rounds = []
    evaluation_rounds = []
    strategy_rounds = []
    strategy_guidance = config.initial_strategy_prompt

    for round_number in range(1, config.iterations + 1):
        generation_round = generate_or_revise_ideas(
            config,
            round_number,
            seed_ideas,
            seed_label,
            idea_pool,
            evaluation_rounds,
            strategy_guidance,
        )
        generation_rounds.append(generation_round)

        evaluation_round = evaluate_and_rank_ideas(
            config,
            round_number,
            idea_pool,
            generation_rounds,
        )
        evaluation_rounds.append(evaluation_round)

        strategy_round = revise_generation_strategy(
            config,
            round_number,
            idea_pool,
            evaluation_rounds,
        )
        strategy_rounds.append(strategy_round)
        strategy_guidance = strategy_round["combined_prompt"]

    result = BrainwritingResult(
        seed_ideas=seed_ideas,
        seed_label=seed_label,
        idea_pool=idea_pool,
        generation_rounds=generation_rounds,
        evaluation_rounds=evaluation_rounds,
        strategy_rounds=strategy_rounds,
        final_idea="",
    )
    result.final_idea = synthesize_final_idea(config, result)
    return result


def output_paths(config):
    output_dir = Path(config.output_dir)
    legacy_html_names = {
        "llm_condition": "llm_debate_transcript.html",
        "hybrid_condition": "hybrid_debate_transcript.html",
    }
    html_name = legacy_html_names.get(
        config.output_prefix,
        f"{config.output_prefix}_transcript.html",
    )
    return (
        output_dir / f"{config.output_prefix}_output.txt",
        output_dir / html_name,
    )


def save_text_output(result, config, condition_title):
    text_path, _ = output_paths(config)

    with open(text_path, "w", encoding="utf-8") as file:
        file.write(condition_title + "\n")
        file.write("=" * 80 + "\n\n")

        file.write("HYPERPARAMETERS\n")
        file.write("=" * 80 + "\n")
        file.write(f"Iterations: {config.iterations}\n")
        file.write(f"Max ranked ideas: {config.max_ranked_ideas}\n")
        file.write(f"Idea temperature: {config.idea_temperature}\n")
        file.write(f"Evaluation temperature: {config.evaluation_temperature}\n")
        file.write(f"Strategy temperature: {config.strategy_temperature}\n")
        file.write(f"Final temperature: {config.final_temperature}\n\n")

        file.write("DESIGN CHALLENGE\n")
        file.write("=" * 80 + "\n")
        file.write(config.design_challenge + "\n\n")

        if result.seed_ideas.strip():
            file.write(result.seed_label.upper() + "\n")
            file.write("=" * 80 + "\n")
            file.write(result.seed_ideas + "\n\n")

        for round_number in range(1, config.iterations + 1):
            file.write(f"ROUND {round_number}: STAGE 1 IDEA GENERATION OR REVISION\n")
            file.write("=" * 80 + "\n")
            file.write(format_dict(result.generation_rounds[round_number - 1]["responses"]))
            file.write("\n\n")

            file.write(f"ROUND {round_number}: STAGE 2 EVALUATION AND RANKING\n")
            file.write("=" * 80 + "\n")
            file.write(format_dict(result.evaluation_rounds[round_number - 1]["responses"]))
            file.write("\n\n")

            file.write(f"ROUND {round_number}: STAGE 3 STRATEGY REVISION\n")
            file.write("=" * 80 + "\n")
            file.write(format_dict(result.strategy_rounds[round_number - 1]["responses"]))
            file.write("\n\nCOMBINED NEXT-GENERATION CONTROL PROMPT\n")
            file.write("-" * 80 + "\n")
            file.write(result.strategy_rounds[round_number - 1]["combined_prompt"])
            file.write("\n\n")

        file.write("FINAL IDEA\n")
        file.write("=" * 80 + "\n")
        file.write(result.final_idea)

    print(f"Saved text output to {text_path}")
    return text_path


def save_html_output(result, config, condition_title):
    _, html_path = output_paths(config)

    def e(value):
        return escape(str(value)).replace("\n", "<br>")

    def role_section(title, responses):
        html = f"<h3>{e(title)}</h3>"
        for agent_name, response in responses.items():
            html += f"""
<div class="card">
  <div class="agent">{e(agent_name)}</div>
  <div>{e(response)}</div>
</div>
"""
        return html

    def combined_strategy_section(strategy_round):
        combined_prompt = strategy_round["combined_prompt"]
        return f"""
<div class="card strategy">
  <div class="agent">Combined next-generation control prompt</div>
  <div>{e(combined_prompt)}</div>
</div>
"""

    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>{e(condition_title)}</title>
<style>
body {{
  font-family: Inter, Arial, sans-serif;
  background: #f8fafc;
  color: #0f172a;
  margin: 0;
  padding: 40px;
}}
.container {{
  max-width: 1080px;
  margin: auto;
}}
.header, .stage {{
  background: white;
  border-radius: 18px;
  padding: 26px;
  margin-bottom: 22px;
  box-shadow: 0 12px 32px rgba(15,23,42,0.07);
}}
h1 {{
  margin: 0;
  font-size: 34px;
}}
h2 {{
  margin-top: 0;
}}
.sub {{
  color: #475569;
  line-height: 1.6;
}}
.card {{
  border: 1px solid #e2e8f0;
  border-left: 5px solid #2563eb;
  border-radius: 14px;
  padding: 16px;
  margin: 12px 0;
  line-height: 1.6;
}}
.agent {{
  color: #1d4ed8;
  font-weight: 800;
  margin-bottom: 8px;
}}
.final {{
  background: #ecfdf5;
  border: 1px solid #bbf7d0;
}}
.final .card {{
  border-left-color: #059669;
}}
.strategy {{
  border-left-color: #7c3aed;
}}
</style>
</head>
<body>
<div class="container">
<div class="header">
  <h1>{e(condition_title)}</h1>
  <p class="sub"><strong>Design Challenge:</strong><br>{e(config.design_challenge)}</p>
  <p class="sub">
    Iterations: {config.iterations} | Max ranked ideas: {config.max_ranked_ideas} |
    Temperatures: generation {config.idea_temperature}, evaluation {config.evaluation_temperature},
    strategy {config.strategy_temperature}, final {config.final_temperature}
  </p>
</div>
"""

    if result.seed_ideas.strip():
        html += f"""
<div class="stage">
  <h2>{e(result.seed_label)}</h2>
  <p class="sub">{e(result.seed_ideas)}</p>
</div>
"""

    for round_number in range(1, config.iterations + 1):
        html += '<div class="stage">'
        html += f"<h2>Round {round_number}</h2>"
        html += role_section(
            "Stage 1: Idea Generation or Revision",
            result.generation_rounds[round_number - 1]["responses"],
        )
        html += role_section(
            "Stage 2: Evaluation, Analysis, and Ranking",
            result.evaluation_rounds[round_number - 1]["responses"],
        )
        html += role_section(
            "Stage 3: Generation Strategy Revision",
            result.strategy_rounds[round_number - 1]["responses"],
        )
        html += combined_strategy_section(result.strategy_rounds[round_number - 1])
        html += "</div>"

    html += f"""
<div class="stage final">
  <h2>Final Idea</h2>
  <div class="card">{e(result.final_idea)}</div>
</div>
</div>
</body>
</html>
"""

    with open(html_path, "w", encoding="utf-8") as file:
        file.write(html)

    print(f"Saved HTML transcript to {html_path}")
    return html_path
