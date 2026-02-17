---
name: changelog
description: Generate a changelog since a specific commit or tag. Use when preparing release notes. Requires a commit hash or tag as input.
---

# Generate Changelog

When the user wants to see what's changed since a specific point, generate a changelog.

## Input Required
The user must provide a **commit hash or tag**. Example: `/changelog abc123` or `/changelog v1.0`

## Step 1: Get Commits

```bash
# List of commits with details
git log --oneline <reference>..HEAD

# Files changed per commit
git log --name-only --pretty=format:"%h %s" <reference>..HEAD
```

## Step 2: Categorize Changes

Group commits into:

### User-Facing (affects how the tools work for users):
- New integrations or features
- Bug fixes users would encounter
- Configuration changes
- Documentation improvements

### Internal (development/maintenance):
- Refactors, code cleanup
- CI changes, dependency updates
- Test improvements
- Skill/config updates

## Step 3: Generate Output

```markdown
## Changelog — [reference] → HEAD

### New Features
- **[Feature Name]** — Brief description

### Improvements
- [Description]

### Bug Fixes
- Fixed [issue description]

### Documentation
- [Description]

### Internal
- [Description]
```

## Guidelines

- **Focus on what changed for users**, not implementation details
- **Be specific**: "Fixed WordPress draft post missing categories" not "Fixed bug"
- **Group related commits** — multiple commits for one feature = one line item
- **Skip noise** — minor formatting, deps bumps, trivial changes
