---
name: upload-image
description: Upload a local image to Blackbird and optionally attach as featured image. Use when Jamie provides an image path. Pass the file path and optionally a post ID.
---

# Upload Image

Upload a local image file to blackbirdpublishing.com via REST API and optionally attach it as a featured image on a post.

## Usage

`/upload-image <file path> [post ID]`

Examples:
- `/upload-image ~/Dropbox/.../Haunted-Waters-Spotlight-Steve-Vernon.jpg`
- `/upload-image ~/Dropbox/.../image.jpg 5480`

## Step 1: Verify the File

Confirm the file exists and check the file type (jpg, png, webp).

## Step 2: Upload via REST API

The MCP `create_media` tool only accepts URLs. For local files, use the direct REST API:

```bash
WP_PASS=$(grep CLAUDE_BLACKBIRD_WP_PASSWORD /Users/jamieferguson/Dropbox/dev/pub-tools/.env | cut -d= -f2) && \
curl -s -X POST "https://blackbirdpublishing.com/wp-json/wp/v2/media" \
  -u "claude:${WP_PASS}" \
  -H 'Content-Disposition: attachment; filename="Clean-Filename.jpg"' \
  -H "Content-Type: image/jpeg" \
  --data-binary "@/full/path/to/file.jpg"
```

**Filename convention:** Use hyphens, no spaces. Example: `Haunted-Waters-Spotlight-Author-Name.jpg`

**Content-Type by extension:**
- `.jpg` / `.jpeg` → `image/jpeg`
- `.png` → `image/png`
- `.webp` → `image/webp`

## Step 3: Set Alt Text

Use `mcp__blackbird-wp__edit_media` to set a descriptive `alt_text` on the uploaded image. Use HTML entities for special characters in alt text.

## Step 4: Attach as Featured Image (if post ID provided)

Use `mcp__blackbird-wp__update_post` with `featured_media` set to the new media ID.

## Step 5: Report

Tell Jamie:
- Media ID and URL
- Dimensions (from the upload response)
- Whether it was attached to a post
- Remind her to assign the image to the correct WP Media folder (not API-accessible for editors)
- Note if the Media File Renamer plugin changed the filename (check `source_url` in response)
