"""ADK entry for Agent Engine. Local CLI and unittest do not need google-adk.

`adk run` / `adk deploy` load this package when google-adk is installed.
Without that extra, importing this package must not fail.
"""

try:
    from .agent import root_agent
except ImportError:
    root_agent = None

__all__ = ["root_agent"]
