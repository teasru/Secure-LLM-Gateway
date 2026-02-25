import re
from app.core.policy_engine import load_policy

def inspect_prompt(prompt: str):
    policy = load_policy()

    for keyword in policy["blocked_keywords"]:
        if keyword.lower() in prompt.lower():
            return False, f"Blocked keyword: {keyword}"

    for pattern in policy["blocked_patterns"]:
        if re.search(pattern, prompt, re.IGNORECASE):
            return False, f"Blocked pattern: {pattern}"

    return True, None
