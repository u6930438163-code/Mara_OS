"""Optional OpenAI Agents SDK integration. Does not execute Linux commands."""
import os

NAMES = ("Aria", "Alex", "Astyria", "Aurelius")

def available():
    try:
        import agents  # noqa: F401
    except ImportError:
        return False
    return bool(os.getenv("OPENAI_API_KEY"))

def run_agent(name, message):
    """Synchronous, tool-free agent run. Intended for controlled backend calls."""
    if name not in NAMES or not isinstance(message, str) or not 1 <= len(message.strip()) <= 8000:
        raise ValueError("Invalid agent or message")
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OpenAI API key is not configured")
    try:
        from agents import Agent, Runner
    except ImportError as exc:
        raise RuntimeError("Install requirements-ai.txt first") from exc
    model = os.getenv("MARA_AGENTS_MODEL", "gpt-4o-mini")
    agent = Agent(name=name, model=model, instructions=(
        "You are a Mara_OS assistant. Respond in Polish. "
        "You have no shell, filesystem, GitHub or MCP tools. "
        "Never claim to have executed a command or completed an action."))
    result = Runner.run_sync(agent, message.strip())
    return {"agent": name, "model": model, "text": str(result.final_output)}
