---
name: review
description: Review a plan, code, or implementation. Use when Jamie asks you to review work. Enforces strict standards — no assumptions, no dismissals.
---

# Peer Review

Review work with zero assumptions. Your job is to find problems. Jamie decides which ones matter.

## Core Principles

**These are non-negotiable. Violating any of them makes the review worthless.**

1. **Never assume something will be handled later.** If it's a problem now, report it now.
2. **Never dismiss findings as "minor."** If it's worth mentioning, it's worth tracking. If it's not worth tracking, don't mention it. There is no middle ground.
3. **Never say "they'll probably fix this during implementation."** You don't know that.
4. **Never say "this is good enough for now."** There is no "for now." Every finding either gets fixed, gets an issue, or gets explicitly accepted by Jamie.
5. **Your job is to find problems, not to decide which ones matter.** Report everything. Jamie makes priority calls.

**Banned phrases** (if you catch yourself writing any of these, rewrite):
- "This is minor and will likely be handled..."
- "Not a blocker, but..."
- "Could be improved later..."
- "This is fine for now..."
- "Low priority..."
- "Nice to have..."
- "Cosmetic issue..."

Replace with: a clear finding statement and let Jamie assign disposition.

## Step 1: Understand the Scope

Ask Jamie (or determine from context) what you're reviewing:
- **A plan** — design doc, implementation approach, architecture decision
- **Code** — committed changes, a PR, or uncommitted work
- **A specific concern** — Jamie wants you to look at something particular

## Step 2: Load Context

**For plan reviews**, read:
- The plan/design document
- Related existing code that the plan will modify (use Glob/Grep to find it)
- CLAUDE.md for project context

**For code reviews**, read:
- The changed files (use `git diff` or read the files directly)
- Any tests for those files
- Related documentation

## Step 3: Evaluate

### For Plans

Check each of these. If you can't verify one, say so explicitly — don't skip it.

| Area | What to check |
|------|---------------|
| **Completeness** | Does the plan cover all stated requirements? Are there requirements it doesn't address? |
| **Correctness** | Does the approach actually solve the problem? Are there logical flaws? |
| **Existing patterns** | Does it follow established codebase patterns? |
| **Edge cases** | What happens with unexpected input? Missing data? Error states? |
| **Security** | Any auth, credential handling, or input validation concerns? |
| **Missing work** | What does the plan NOT mention that it should? |

### For Code

| Area | What to check |
|------|---------------|
| **Requirements** | Does the code fulfill all stated requirements? |
| **Tests** | Do tests exist? Do they cover the actual changed behavior? |
| **Error handling** | Are errors handled? Are error messages helpful? |
| **Security** | Credentials protected? User input validated? |
| **Patterns** | Does it follow established patterns in the codebase? |
| **Edge cases** | What inputs would break this? |

## Step 4: Classify Findings

Every finding gets ONE of these classifications:

| Classification | Meaning | What happens |
|----------------|---------|--------------|
| **BLOCKER** | Must be fixed before this work ships | Fix before merge |
| **ISSUE** | Real problem, but can be tracked separately | Create a GitHub issue |
| **QUESTION** | You're not sure — need clarification | Jamie decides |

**There is no "suggestion" or "nice-to-have" classification.** If it matters, it's one of the three above. If it doesn't matter, don't include it.

## Step 5: Generate Report

Use this exact format:

```
## Peer Review — [What's being reviewed]

**Scope**: [Plan / Code changes / specific files]

### Summary

[2-3 sentences: What does this work do? Does the overall approach make sense?]

### Findings

#### BLOCKERS (must fix before shipping)

1. **[Area]**: Clear description of the problem.
   - **Where**: [file:line or section of plan]
   - **Why it matters**: [What goes wrong if this isn't fixed]
   - **Suggested fix**: [How to fix it, if you have a recommendation]

(or "None")

#### ISSUES (track separately)

1. **[Area]**: Clear description of the problem.
   - **Where**: [file:line or section of plan]
   - **Why it matters**: [What goes wrong if this isn't addressed]

(or "None")

#### QUESTIONS (need clarification)

1. **[Area]**: What you're unsure about.
   - **Context**: [What you've checked so far]
   - **Options**: [If you see multiple interpretations]

(or "None")

### What Looks Good

[Briefly note things done well — this isn't just about finding problems.
But keep it honest. Don't pad this section to soften the findings.]

### Self-Reflection

[Before writing your verdict, pause and ask yourself:]

- "Did I actually read the code/plan, or did I skim and assume?"
- "Am I approving because it's good, or because I didn't look hard enough?"
- "If this ships and breaks, would I be surprised — or did I see a warning sign and rationalize it away?"
- "Did I soften any finding to be polite?"

[Write what you honestly think.]

### Verdict

**APPROVE** — No blockers. [N issues to track, N questions to clarify.]

— or —

**CHANGES NEEDED** — N blockers must be addressed before shipping.

— or —

**NEEDS DISCUSSION** — Fundamental approach questions that Jamie should weigh in on before proceeding.
```

## Guidelines

- **Read the actual code/plan.** Don't review based on descriptions or summaries.
- **Verify, don't assume.** If the plan says "we'll add tests," check whether the test plan actually covers the behavior.
- **Be direct.** "This will break when X is null" is better than "It might be worth considering the case where X could potentially be null."
- **One finding per item.** Don't bundle multiple issues into one finding.
- **Credit good work.** If the approach is solid, say so.
