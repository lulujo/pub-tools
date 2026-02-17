---
name: since
description: Summarize work completed since a specific date or commit. Use for internal progress tracking and reporting.
---

# Progress Summary Since Date

Generate a categorized summary of work completed since a specific point in time. For internal tracking and progress reporting.

## Input Formats

The user provides one of:
- **Date**: `/since 2026-01-01` or `/since jan 1`
- **Relative**: `/since 2w` (2 weeks), `/since 1m` (1 month)
- **Commit**: `/since abc123`

## Step 1: Get Commits

```bash
# For date-based
git log --since="<date>" --oneline

# For commit-based
git log <hash>..HEAD --oneline

# With file details
git log --since="<date>" --name-only --pretty=format:"%h %s"
```

### For relative time parsing:
- `1w` = "1 week ago"
- `2w` = "2 weeks ago"
- `1m` = "1 month ago"
- `3d` = "3 days ago"

## Step 2: Categorize Work

Group commits into these categories:

### Features Added (new functionality)
- New integrations
- New tools or scripts
- New skills

### Improvements (enhancements to existing work)
- Performance improvements
- UX improvements
- Code quality improvements

### Bug Fixes
- Integration fixes
- Configuration fixes

### Documentation
- Setup guides, how-tos
- CLAUDE.md updates
- Plan/design documents

### Infrastructure
- CI/CD changes
- Dependency updates
- Tooling improvements

## Step 3: Generate Summary

```markdown
## Progress Since [DATE]

**Period**: [start date] → [end date]
**Commits**: [count]

### Features Added
- **[Feature Name]** — Brief description
- **[Feature Name]** — Brief description

### Improvements
- [Description]

### Bug Fixes
- Fixed [issue description]

### Documentation
- [Description]

### Infrastructure
- [Description]
```

## Guidelines

1. **Be concise** — One line per item, expand only for significant features
2. **Group related commits** — Multiple commits for one feature = one line item
3. **Skip noise** — Minor formatting, trivial docs changes
4. **Highlight metrics** — Include before/after numbers when available
