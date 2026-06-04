---
name: safe-github-publish
description: Safely publish a local app or codebase to GitHub. Use when the user asks to commit, push, upload, sync, publish, or verify code on GitHub, especially when the project has env files, API keys, Feishu tokens, generated outputs, local virtual environments, or when GitHub CLI/local git credentials may be missing and a GitHub connector/plugin might be used.
---

# Safe GitHub Publish

## Purpose

Publish code to GitHub without leaking secrets, losing local work, or assuming the remote is correct just because a write command succeeded.

## Non-Negotiables

- Never commit `.env`, local credentials, generated outputs, virtual environments, caches, or private screenshots unless explicitly required and safe.
- Scan for secrets before staging and before finalizing.
- Verify the remote after pushing or connector-based writes.
- Do not overwrite user changes or reset local work destructively without explicit approval.
- If using a connector/plugin to write files, validate the remote content after the write.

## Workflow

1. Inspect state.
   - Check branch, remote URL, staged changes, unstaged changes, and untracked files.
   - Identify ignored files and sensitive files.

2. Protect secrets.
   - Ensure `.env`, `.venv`, `__pycache__`, generated outputs, and local temp files are ignored.
   - Keep `.env.example` placeholders safe.
   - Run targeted scans for known token patterns and project-specific secrets.

3. Verify locally.
   - Run lightweight compile/lint/tests appropriate to the project.
   - For apps, verify the entry point and dependency list are present.
   - For skills, validate required `SKILL.md` frontmatter.

4. Stage and commit.
   - Stage explicit intended files, not broad unknown paths, when sensitive files exist.
   - Use a concise commit message describing the user-facing change.
   - Do not include unrelated local changes.

5. Push or publish.
   - Prefer normal `git push` when credentials are available.
   - If local credentials are missing, use a GitHub connector/plugin only when it can preserve content safely.
   - For connector uploads, avoid raw long non-ASCII file uploads if the connector has shown encoding issues; use normal git, base64 with verification, or ASCII-equivalent source where appropriate.

6. Verify remote.
   - Fetch or read back the remote commit.
   - Compare file lists and key diffs.
   - Compile or inspect remote-fetched critical files if possible.
   - Confirm local branch and remote branch are aligned, or explain any intentional divergence.

## Secret Scan Examples

Search for project-specific values and common API-key patterns:

```bash
rg -n "sk-[A-Za-z0-9]|APP_SECRET|ACCESS_TOKEN|BITABLE|table_id|app_token" . --glob '!outputs/**' --glob '!.venv/**'
```

If a real secret is found in a tracked file, remove it before committing. If already pushed, rotate the secret.

## Final Report

Report:

```text
GitHub status:
Latest commit:
Files published:
Secrets check:
Verification:
Remaining action:
```

If a push is blocked by auth, state the exact blocking reason and offer the safest alternative.

