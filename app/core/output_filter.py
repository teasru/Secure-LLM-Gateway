import re
from app.core.policy_engine import load_policy


def filter_output(response: str):
    """
    Post-process LLM output to redact sensitive content
    based on active policy rules.
    """

    policy = load_policy()

    # Redact blocked keywords
    for keyword in policy.get("blocked_keywords", []):
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        response = pattern.sub("[REDACTED]", response)

    # Example: detect possible API keys or secrets (basic heuristic)
    secret_patterns = [
        r"sk-[A-Za-z0-9]{20,}",      # OpenAI-style key
        r"AKIA[0-9A-Z]{16}",         # AWS access key
        r"-----BEGIN PRIVATE KEY-----"
    ]

    for pattern in secret_patterns:
        response = re.sub(pattern, "[REDACTED_SECRET]", response)

    return response
