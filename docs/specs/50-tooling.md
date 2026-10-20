# Shipped code

What the code users run must hold, whatever tools develop it. The development tooling itself (ruff,
pytest, uv, the commit gate) is not a spec rule: it is recorded in D-048 and in CLAUDE.md.

### TOOL-004 · Shipped code stays standard library
Given the code under `hooks/` and `skills/`
When its imports are checked
Then it imports nothing outside the standard library; only `tests/` may import pytest (D-048).
