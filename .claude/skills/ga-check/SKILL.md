---
name: ga-check
description: Self-audit whether your session's work is ready to ship. Run before declaring work complete or when asked "is this ready?"
---

# Quality Self-Audit

Run a targeted quality audit of your changes. Catch gaps before Jamie has to ask.

## Step 1: Identify What Changed

Run in parallel:

```bash
# All files this session touched (committed + uncommitted)
(git diff HEAD --name-only; git log main..HEAD --name-only --pretty=format:"") | sort -u | grep -v '^$'
```

```bash
# Quick view of uncommitted state
git status --short
```

Collect the **unique list of changed files** for review.

## Step 2: Classify Change Types

Examine the file list and mark ALL categories that apply:

| Category | Triggered by |
|---|---|
| **integration** | Files in `integrations/` (WordPress, Buffer, etc.) |
| **config** | CLAUDE.md, .gitignore, skill files, MCP config |
| **docs** | Files in `docs/`, README, setup guides |
| **scripts** | Shell scripts, automation tools |
| **tests** | Test files |

## Step 3: Run Targeted Checks

**Run checks appropriate to the change type:**

### If `integration` or `scripts`:
- Check for hardcoded credentials, API keys, or URLs that should be configurable
- Check for proper error handling on API calls
- Verify any URLs or endpoints are correct

### If `config`:
- Verify CLAUDE.md is accurate and reflects current project state
- Check .gitignore covers sensitive files

### If `docs`:
- Verify instructions are accurate and complete
- Check that referenced files/paths actually exist

### Content-specific checks (always run when output includes WordPress content):
- **Curly quotes:** Verify "curly quotes" not "straight quotes" in all content — titles, dialogue, emphasis, everything
- **Em dashes:** No spaces around em dashes mid-sentence (grief—and loss, not grief — and loss)
- **WordPress taxonomy:** Categories and tags match what's defined in `integrations/wordpress/CONTENT_PLAN.md`
- **SEO fields:** When Rank Math integration is active, verify meta title, description, and focus keyword are set and sensible
- **Featured image:** Verify image is attached and assigned to the correct WP Media folder
- **CTA reminder:** Every post must end with `[ADD CTA PATTERN]`
- **Author voice:** Content from author responses must be preserved exactly — no edits to word choices, Canadian spellings, etc.

## Step 4: Manual Review of Changed Files

Read through the changed files and check for:

1. **TODO/FIXME comments** — Indicate incomplete work. Blocker.
2. **Hardcoded credentials or secrets** — Even in examples. Critical blocker.
3. **Hardcoded values** — Magic numbers, hardcoded URLs that should be configurable.
4. **Missing error handling** — API calls without error handling, missing fallbacks.
5. **Inconsistent formatting** — Straight quotes where curly quotes should be, spacing issues.

## Step 5: Self-Reflection

Before generating the report, pause and ask yourself honestly:

**"Am I happy with this?"**

This catches things that fall through the structured checklist:
- Gut feelings about code quality or design
- Concerns you noticed but rationalized away
- Edge cases that aren't handled
- Documentation that's technically present but unclear

If you can't honestly say "yes, I'm happy with this" — it's not ready.

## Step 6: Flag Pre-Existing Issues

If you noticed issues that **predate your work** while reading code around your changes, report them separately. These don't block your verdict, but Jamie needs to know about them.

Format:
```
### Pre-Existing Issues Noticed
- **[file:line]** Brief description of what's wrong
- (or "None noticed")
```

## Step 7: Generate Report

Use this exact format:

```
## Quality Audit Report — Brief title of what was built/fixed

### Scope
- **Files changed**: N files
- **Categories**: [integration, docs, config, ...]
- **Commits**: N commits + uncommitted changes

### Review Findings
| Area | Result |
|------|--------|
| Hardcoded credentials | PASS/FAIL |
| Error handling | PASS/FAIL |
| Documentation accuracy | PASS/FAIL |
| Formatting (quotes, em dashes) | PASS/FAIL |
| WordPress taxonomy | PASS/FAIL/N/A |
| SEO fields (Rank Math) | PASS/FAIL/N/A |
| Content voice preserved | PASS/FAIL/N/A |

### Manual Review
- [Findings, or "No issues found"]

### Self-Reflection
[Answer honestly: "Am I happy with this?" If not, explain what's bothering you.]

### Pre-Existing Issues Noticed
- [Items, or "None noticed"]

### Verdict

🟢 **READY** — All checks pass, no findings.

— or —

🔴 **NOT READY** — N items to address:

1. **[BLOCKER]** Description
2. **[WARNING]** Description
```

## Verdict Criteria

**READY** requires ALL of:
- No hardcoded credentials or secrets
- Error handling present on external API calls
- Documentation is accurate
- Formatting is consistent (curly quotes, em dashes)
- WordPress taxonomy matches CONTENT_PLAN.md (when applicable)
- SEO fields are set and sensible (when Rank Math integration is active)
- Author voice preserved in interview/response content
- **You can honestly say "Yes, I'm happy with this"**

**NOT READY** if ANY of:
- Hardcoded credentials → **BLOCKER**
- Missing error handling on API calls → **BLOCKER**
- TODO/FIXME indicating unfinished work → **BLOCKER**
- Self-reflection reveals unaddressed concerns → **BLOCKER**
- Straight quotes in published content → **BLOCKER**
- Author voice edited (word choices changed, spellings "corrected") → **BLOCKER**
- Missing CTA reminder on post → **BLOCKER**
- Inaccurate documentation → **WARNING**
- Missing SEO fields → **WARNING**
- Taxonomy mismatch → **WARNING**

## Guidelines

- **Be honest.** The point is catching gaps before Jamie does.
- **Be specific.** Not "missing error handling" — say which file and which call.
- **Report what you see.** Pre-existing issues aren't your fault, but ignoring them is.
