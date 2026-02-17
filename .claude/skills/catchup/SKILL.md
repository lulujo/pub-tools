---
name: catchup
description: Summarize current project status and recent work. Use when user returns after a break or asks "what's happening" or "catch me up".
---

# Catch Up on Current State

When the user wants to understand the current state of the project, gather information then provide a structured summary.

## Step 1: Gather Information (run in parallel)
- Read `CLAUDE.md` for current project status
- Run: `git log --oneline -20` (recent commits)
- Run: `git status`
- Run: `git branch -a` (see active branches)

## Step 2: Provide Summary

Use this output format:

```
## Project Catchup

### Recent Work
[Group last ~20 commits by theme: Features, Fixes, Docs, Config]
[Skip routine items like minor formatting changes]

### Current Branch State
- Branch: [name]
- Status: [ahead/behind origin]
- Uncommitted: [count of modified files, not individual filenames]

### Items Needing Attention
[Flag any of these if present:]
- Unpushed commits (X commits ahead)
- Uncommitted changes
- Stale branches
- TODOs or known issues from CLAUDE.md
```

Keep the summary concise and actionable.
