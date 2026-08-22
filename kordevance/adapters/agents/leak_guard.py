import logging
import re

from pydantic_ai.messages import ModelMessage, ModelResponse, TextPart

logger = logging.getLogger(__name__)

# Vocabulary that only makes sense if the model is describing its own implementation rather
# than answering the user. Prompt instructions ask every agent not to say these things, but
# instructions are probabilistic

# DISCLAIMER: This pattern surely doesn't cover all cases
_LEAK_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\b(sub-?agent|specialist|orchestrat\w*|handoff|hand off|routing layer|triage model)\b",
        r"\b(system prompt|instructions say|my instructions|i('m| am) instructed)\b",
        r"\bi don'?t have access to (a |the )?tool\b",
        r"\b(pydantic[- ]?ai|tool call|function call|deps_type|RunContext)\b",
        r"\b(gpt-|claude-|gemini-|llama-)\w*\b",
    )
)

_FALLBACK_REPLY = "I can't help with that part. Let me know what you're trying to do and I'll take it from there."


def sanitize_reply(text: str) -> str:
    """Deterministic backstop against any agent describing its own internals to the user.

    Returns `text` unchanged if it looks clean, otherwise a generic fallback. Any match is
    logged so the leaking prompt can be tightened, but the user never sees the leaked text.
    """
    for pattern in _LEAK_PATTERNS:
        match = pattern.search(text)
        if match:
            logger.warning("Blocked a reply that leaked internal details (matched %r): %r", match.group(0), text)
            return _FALLBACK_REPLY
    return text


def sanitize_agent_output(output: str, new_messages: list[ModelMessage]) -> str:
    """Sanitize an agent's final text reply, and scrub the same text out of the messages that
    are about to be persisted to conversation history .

    Returns the (possibly replaced) reply text. Mutates `new_messages` in place.
    """
    sanitized = sanitize_reply(output)
    if sanitized == output:
        return output

    for message in new_messages:
        if not isinstance(message, ModelResponse):
            continue
        for part in message.parts:
            if isinstance(part, TextPart) and part.content == output:
                part.content = sanitized
    return sanitized
