---
name: comms
description: Open a session-comms discussion file. Use when Jamie says to check, review, or respond to a session-comms thread. Pass the filename (without path) as the argument.
---

# Session Comms

Open and engage with a multi-session discussion thread.

## Usage

`/comms <filename>` — e.g., `/comms PUB-5` or `/comms wordpress-taxonomy-plan`

## Step 1: Find and Read the File

**IMPORTANT: Always try ALL locations before giving up.** Tell Jamie which path you found (or tried).

Search these paths in order:

1. `docs/session-comms/<filename>.md` (pub-tools — for local discussions)
2. `docs/session-comms/<filename>` (if extension was included)
3. `~/Dropbox/dev/inkwren/inkwren-develop/internal-docs/session-comms/<filename>.md` (Inkwren — for cross-team discussions)
4. `~/Dropbox/dev/inkwren/inkwren-develop/internal-docs/session-comms/<filename>` (if extension was included)
5. `~/Dropbox/dev/calliopelabs/rookery/docs/session-comms/<filename>.md` (Rookery — for cross-team discussions)
6. `~/Dropbox/dev/calliopelabs/rookery/docs/session-comms/<filename>` (if extension was included)

When you find the file, say where: "Found in pub-tools session-comms", "Found in Inkwren session-comms (cross-team)", or "Found in Rookery session-comms (cross-team)".

If not found in any location, tell Jamie: "File `<filename>` not found in pub-tools, Inkwren, or Rookery session-comms."

If the file doesn't exist and Jamie's intent seems to be creating a new thread, create it in `docs/session-comms/` with this template:

```markdown
# Topic Title

## Plan / Content
**Author:** [your name]

(Content here)

---

## Discussion
```

## Step 2: Engage

After reading the file, follow Jamie's instructions. Common patterns:

- **"Check the discussion"** — Read the thread, summarize what's happened, ask Jamie what she wants you to do
- **"Review the plan"** — Read the plan section, then use the `/review` skill's standards to evaluate it. Write your review as a comment in the Discussion section.
- **"Respond to the review"** — Read the review comments, address each finding, update your plan in the Plan/Content section, and add a comment explaining what you changed
- **"Write a plan for X"** — Create the file with your plan in the Plan/Content section
- **"Add your thoughts"** — Read the thread and append your comment

## Step 3: Write Your Comment

When adding to the discussion, append to the end of the file:

```markdown
**[Your Name] · YYYY-MM-DD**

(Your comment here)
```

**Rules:**
- **Append only** — never edit another session's comments
- **Update the Plan/Content section** if it's your artifact and you're revising it
- **Be specific** — other sessions will read this asynchronously without your context
