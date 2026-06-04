---
name: zero-to-one-mobile-workflow-app
description: Turn a user's real repeated workflow into a first usable mobile-friendly app. Use when the user has a manual process, screenshots, spreadsheets, chat prompts, forms, files, or operational decisions and wants to build a new app/tool from 0 to 1, especially when the path is unclear and the goal is a practical mobile-usable workflow rather than a landing page.
---

# Zero To One Mobile Workflow App

## Purpose

Build the first useful version of an app from the user's real workflow. Start from the repeated job, not from UI ideas or frameworks. The first milestone is a working loop the user can run on a phone or browser.

## First Principles

- Identify the real repeated action: what the user does, when, with what inputs, and what decision/output they need.
- Prefer the shortest useful loop over a polished broad product.
- Keep human review where the output affects money, records, permissions, or irreversible actions.
- Do not build a landing page unless explicitly requested. Build the actual working screen first.
- A mobile-friendly app means readable, tappable, and usable on a phone; it does not always mean a native mobile app.

## Workflow

1. Map the current manual workflow.
   - Inputs: screenshots, files, text, APIs, databases, messages, forms.
   - Transformations: OCR, matching, calculation, validation, enrichment, analysis.
   - Outputs: table records, report, recommendation, file, notification, dashboard.
   - Human decision points: approve, edit, reject, execute.

2. Define the first closed loop.
   - Choose one daily or frequent scenario.
   - Require only the minimum fields needed to complete it.
   - Include a fallback path when automation fails, such as manual edit or pasted text.

3. Choose the storage layer.
   - For early personal/team apps, prefer a simple online table, Bitable, spreadsheet, SQLite, or small database.
   - Keep secrets in env files or platform secrets, never in committed code.
   - Store normalized records, not raw UI text, unless raw text is needed for audit.

4. Build the app surface.
   - First screen should be the working tool: upload/input, editable review, write/save, result.
   - Make controls obvious and action-oriented.
   - Show status, counts, and validation failures close to the action.
   - Avoid decorative complexity until the loop works.

5. Verify end to end.
   - Use realistic sample inputs.
   - Check the written records or generated outputs, not only the UI success message.
   - Confirm the app works after reload and on a mobile viewport when relevant.

6. Publish and preserve.
   - Commit only source, docs, and safe examples.
   - Ignore env files, local caches, generated outputs, and virtual environments.
   - Write a concise README with run steps and configuration placeholders.

## Output Shape

When planning or reporting progress, use:

```text
当前最短闭环：
输入：
处理：
人工确认：
输出：
下一步：
```

When building, implement the loop instead of only proposing it unless the user explicitly asks for discussion only.

