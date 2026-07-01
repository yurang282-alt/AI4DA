# Project Context

## One-Liner

AI4DA is a local ETF daily-tracking assistant that turns screenshots into editable records, writes reviewed data into Feishu, and produces next-day decision support while keeping the final investment action manual.

## User And Problem

- Target user: The user as a self-directed investor tracking a fixed ETF watchlist.
- Real problem: Daily screenshot collection, data transcription, and next-day review are repetitive and error-prone.
- Current workaround: Manual screenshot reading, spreadsheet updates, and ad hoc analysis.
- Success signal: The user can upload the daily screenshots, correct the extracted table, write reviewed data into Feishu, and get a next-day reference readout without trusting automation blindly.

## Product Shape

- Core flow: Upload price and holding screenshots -> review extracted rows -> write corrected data to Feishu -> read next-day support output -> manually decide what to do.
- Must-have: Screenshot ingestion, editable table, Feishu write path, ETF watchlist mapping, and explicit human confirmation before any record is trusted.
- Explicit non-goals: Auto trading, unattended execution, guaranteed returns, or replacing manual investment judgment.
- Important states: OCR/edit review, Feishu CLI write mode, no-OpenAI fallback, no-Feishu fallback, and manual final confirmation.

## Current Status

- Stage: Local decision-support workflow is documented and runnable.
- Working version: The README defines the screenshot flow, Feishu Bitable write path, ETF watchlist, CLI-preferred write mode, and optional OpenAI-assisted analysis.
- Local state: Run via Python virtualenv and Streamlit from the project root.
- GitHub state: Latest local commit seen on 2026-06-04 is `96bc4d6 Add Codex workflow skills`. Working tree was clean at scan time.
- Deployment state: No user-facing cloud deployment is part of the current design.
- In-app/release state: This is a private local workflow, not a publishable finance product.

## Architecture

- Client/platform: Local Streamlit app.
- Backend/data: Local screenshot/OCR workflow plus Feishu CLI/Bitable output.
- Auth/identity: Local user workflow; no multi-user auth model.
- Storage: Local files, reviewed rows, and Feishu Bitable as the durable record surface.
- External services: Optional OpenAI for analysis, Feishu CLI or app credentials for writes.
- Key constraints: Never automate trades. Keep privileged Feishu or model secrets out of the UI. Treat every generated suggestion as advisory only.

## Decisions

- Chosen path: Keep AI4DA as a decision-support tool only.
- Rejected paths: Automatic investment actions, public release, or positioning this as financial advice software.
- Why: The product can save mechanical work, but investment risk and data-quality risk are too high to delegate final action.
- Revisit trigger: Only if the user wants a stricter internal audit trail or better ingestion reliability; not to make it auto-trade.

## Risks

- Product risk: If ingestion errors are frequent, the workflow adds distrust instead of saving time.
- Technical risk: OCR alias mapping and Feishu write assumptions can silently produce bad records if not reviewed.
- Data/privacy risk: Holdings and cash data are sensitive financial information.
- Release risk: There should be no ambiguity between reviewed data, generated suggestion, and final user action.

## Next Actions

- Now: Keep the tool in reviewed-manual mode and verify ingestion reliability before relying on the output.
- Later: Add a clearer audit trail for corrected rows and decision notes if daily use becomes stable.
- Blocked: No blocker for local use, but this should not move toward unattended execution.

## Useful Commands Or Links

- Local run: `streamlit run app.py`
- Environment setup: `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
- Project root: `/Users/bytedance/AI4DA`
- Main reference: `README.md`

## Design Agent Governance

Source of truth: /Users/bytedance/Documents/Codex/app-design-agent-routing-rule.md and /Users/bytedance/Documents/Codex/agent-briefs/design-director-agent.md.

AI4DA should use the Product Design Director Agent whenever a new user-facing surface, UI change, prototype, redesign, or friend/team-facing release is discussed.

Design Agent intervention check:

```text
设计 Agent 介入判断：
- 是否有用户界面：
- 是否面向真实用户 / 朋友 / 团队：
- 是否需要和其他 App 形成明显差异：
- 是否有强场景气质：
- 是否会影响核心流程或首次体验：
- 是否已有截图/原型/页面可审：
- 介入级别：L0 / L1 / L2 / L3 / L4
- 本次产出：
```

Intervention levels:

- L0: no design agent for pure backend, scripts, data processing, or tiny non-UI fixes.
- L1: design DNA for a new user-facing app or early product idea.
- L2: design audit for an existing UI, screenshot, URL, or runnable demo.
- L3: redesign direction for core pages, onboarding, navigation, or first-use experience.
- L4: portfolio design system when multiple apps need shared components but distinct visual identities.


This project's design DNA:

- Product identity: ETF screenshot ingestion and decision-support workflow.
- Desired feeling: Restrained, risk-first, manual-decision support.
- Design direction: Clear risk flags, provenance, confidence, conservative dashboard language.
- Avoid: Trading-game UI, profit-chasing visuals, automated-advice tone.
- First design focus: Keep user decision responsibility visible.

Boundaries:

- The design agent defines design DNA, audits UI/UX fit, and produces design recommendations.
- The main product partner + CTO agent still decides priority, product scope, architecture, release, and whether implementation should start.
- The design agent does not publish, merge, deploy, change databases, or change permissions by default.

