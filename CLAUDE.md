# CLAUDE.md

Instructions for Claude Code when working in this repository/vault.

## Token-Saving Rules (Strict)

These rules apply to every session in this vault, without exception:

1. **Be concise.** Keep all responses as short as possible while still being correct and complete. No preambles, no restating the request, no unnecessary elaboration.
2. **Output only modified parts.** When changing code or text, show/apply only the diff or the specific changed section — never regenerate or reprint an entire file/document unless the user explicitly asks for the full file.
3. **Minimize token usage aggressively:**
   - Read only the relevant portions of files (use targeted reads, not full-file dumps), unless full context is required for correctness.
   - Avoid re-reading files or re-fetching data already available in the current session.
   - Skip lengthy explanations of reasoning or process; report results and next steps only.
   - Avoid speculative or exploratory output (e.g. multiple alternative solutions) unless requested.
   - Batch independent tool calls together instead of issuing them serially.
   - Use `/clear` or `/compact` proactively when a session's context is no longer needed in full.
4. **No filler.** Do not add summaries, sign-offs, or commentary beyond what's needed to convey the result.
5. **Ask before expanding scope.** If a task could be done narrowly or broadly, default to the narrow interpretation and only expand if explicitly asked.

Refer to `Claude_Token_Saving_Guide.md` in this vault for the full rationale and detailed practices behind these rules.
