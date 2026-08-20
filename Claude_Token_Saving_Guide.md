# Claude Code Token-Saving Guide

Practical methods for minimizing token consumption (and cost) when working with Claude Code.

## 1. Manage Context Actively

- **Start focused sessions.** Don't let one conversation sprawl across unrelated tasks — open a new session per task so old, irrelevant context isn't dragged along.
- **Use `/clear` between unrelated tasks** instead of continuing in the same long thread.
- **Use `/compact`** when a session must continue but has accumulated a lot of resolved back-and-forth.
- **Avoid re-reading large files repeatedly.** Once a file's contents are known in-session, refer back to it by path/line instead of asking for a full re-read.

## 2. Be Precise With File Reads

- **Read only what you need.** Use `offset`/`limit` on large files instead of loading the whole thing.
- **Prefer targeted search tools** (grep/glob-style search) over reading entire directories to find something — search first, then read only the matching sections.
- **Avoid dumping huge command output** into context (e.g. verbose build logs) — filter or pipe to show only the relevant lines.

## 3. Prefer Diffs Over Full Rewrites

- **Output only the changed parts of code/text**, not the entire file, whenever an edit is being described or applied.
- **Use edit/patch-style operations** rather than "regenerate the whole file" when only a small change is needed.
- **Keep commit messages and explanations short** — state what changed and why in 1–2 sentences, not paragraphs.

## 4. Keep Responses Concise

- **Answer directly.** Skip preambles, restating the question, or summarizing what you're about to do at length.
- **Avoid unnecessary elaboration** — no headers/sections for simple answers, no exhaustive alternative-approaches discussion unless asked.
- **Skip verbose narration** of intermediate steps; report results, not a full trace of reasoning.

## 5. Delegate and Parallelize Wisely

- **Use subagents only for large, independent research tasks** that would otherwise bloat the main context — not for small lookups doable directly.
- **Batch independent tool calls together** rather than issuing them one at a time across multiple turns, reducing round-trip overhead.

## 6. Use Caching and Reuse

- **Take advantage of prompt caching** for large, stable context (e.g. system prompts, reference docs) that's reused across turns.
- **Reuse prior results** already established in the conversation instead of re-deriving or re-fetching them.

## 7. Scope Requests Tightly

- **Ask for exactly what's needed** — a single function fix rather than "review and improve this whole file," if that's all that's required.
- **Avoid speculative/exploratory generation** ("show me 5 possible implementations") unless genuinely needed — ask for one solid approach first.

## 8. Configuration-Level Controls

- **Use `CLAUDE.md`** to encode persistent preferences (conciseness, diff-only output) so they don't need to be repeated every session.
- **Limit tool/context auto-loading** (e.g. large MCP resource dumps, broad directory listings) to only what's relevant to the current task.

---

*Following these practices reduces both token usage and cost while keeping responses fast and relevant.*
