"""Compatibility entry point for the original explicit-post collector. MIT licensed."""

from agentic_gtm.workflows.linkedin_engagers import (  # noqa: F401
    BASE_URL,
    collect,
    create_plan,
    linkedin_url,
    load_plan,
    main,
    normalize,
    post_url,
    write_json,
)

if __name__ == "__main__":
    main()
