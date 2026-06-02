from src.role_based_pipeline import (
    build_arg_parser,
    config_from_args,
    run_role_based_brainwriting,
    save_html_output,
    save_text_output,
)


CONDITION_TITLE = "LLM-ONLY ROLE-BASED BRAINWRITING CONDITION"


def main():
    parser = build_arg_parser(
        default_output_prefix="llm_condition",
        description="Run the LLM-only role-based brainwriting pipeline.",
    )
    config = config_from_args(parser.parse_args())

    result = run_role_based_brainwriting(config)

    save_text_output(result, config, CONDITION_TITLE)
    save_html_output(result, config, CONDITION_TITLE)

    print("\n========== FINAL LLM-ONLY IDEA ==========")
    print(result.final_idea)


if __name__ == "__main__":
    main()
