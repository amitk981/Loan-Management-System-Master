# ADR-0001: Use Ralph AFK Workflow

## Status
Accepted

## Context
The repository needs a repeatable agent-driven development workflow that survives lost chat history and supports Codex, Claude Code, or future agents.

## Decision
Adopt Ralph v2.1 as a repo-memory operating system using `docs/working/`, `docs/slices/`, `.ralph/`, `AGENTS.md`, `CLAUDE.md`, and bash scripts under `scripts/`.

## Consequences
- Future work should be planned as small vertical slices.
- `docs/source/` remains read-only.
- Normal AFK runs use worktrees and run folders.
- Quality gates, evidence, risk assessment, review packets, handoff, progress, and state are required before completion.
