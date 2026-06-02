import os

from src.role_based_pipeline import (
    build_arg_parser,
    config_from_args,
    run_role_based_brainwriting,
    save_html_output,
    save_text_output,
)


CONDITION_TITLE = "HYBRID HUMAN IDEAS + ROLE-BASED LLM BRAINWRITING CONDITION"
HUMAN_IDEAS_PATH = "human_ideas_input.txt"


def read_human_ideas():
    if not os.path.exists(HUMAN_IDEAS_PATH):
        raise FileNotFoundError(
            "human_ideas_input.txt not found. Create it and paste the anonymous human ideas inside."
        )

    with open(HUMAN_IDEAS_PATH, "r", encoding="utf-8") as file:
        return file.read()


def main():
    parser = build_arg_parser(
        default_output_prefix="hybrid_condition",
        description="Run the human-seeded role-based LLM brainwriting pipeline.",
    )
    config = config_from_args(parser.parse_args())
    human_ideas = read_human_ideas()

    result = run_role_based_brainwriting(
        config,
        seed_ideas=human_ideas,
        seed_label="Anonymous human ideas",
    )

    save_text_output(result, config, CONDITION_TITLE)
    save_html_output(result, config, CONDITION_TITLE)

    print("\n========== FINAL HYBRID IDEA ==========")
    print(result.final_idea)


if __name__ == "__main__":
    main()
