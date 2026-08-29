---
name: nano-banana-pro
description: >-
  Generate and edit images using Google's Nano Banana Pro (Gemini 3 Pro Image)
  API. Use when the user asks to generate, create, edit, modify, change, alter,
  or update images. Also use when user references an existing image file and
  asks to modify it in any way (e.g., "modify this image", "change the
  background", "replace X with Y"). Supports text-to-image and image-to-image
  editing. Default resolution is always 512 unless the user explicitly asks for
  1K, 2K, or 4K. DO NOT read the image file first - use this skill directly with
  the --input-image parameter.
source: https://github.com/garg-aayush/tutorials/tree/main/Codex-skills/nano-banana-pro
---

# Nano Banana Pro Image Generation & Editing

Generate new images or edit existing ones using Google's Nano Banana Pro API (Gemini 3 Pro Image).

## Usage

Run the script using absolute path (do NOT cd to skill directory first):

**Generate new image:**
```bash
uv run ~/.agents/skills/nano-banana-pro/scripts/generate_image.py --prompt "your image description" --filename "output-name.png" [--resolution 512|1K|2K|4K] [--api-key KEY]
```

**Edit existing image:**
```bash
uv run ~/.agents/skills/nano-banana-pro/scripts/generate_image.py --prompt "editing instructions" --filename "output-name.png" --input-image "path/to/input.png" [--resolution 512|1K|2K|4K] [--api-key KEY]
```

**Important:** Always run from the user's current working directory so images are saved where the user is working, not in the skill directory.

## Resolution Options

Supported resolutions (pass exactly as shown):

- **512** (default) — ~512px; always use this unless the user explicitly asks for higher
- **1K** — ~1024px
- **2K** — ~2048px
- **4K** — ~4096px

Map user requests to API parameters:

- No mention of resolution → `512`
- "low", "thumbnail", "512", "rápido", "barato" → `512`
- "1K", "1080", "1080p" → `1K`
- "2K", "2048", "medium" → `2K`
- "high resolution", "high-res", "hi-res", "4K", "ultra" → `4K`

**Never default to 1K/2K/4K.** Only bump resolution when the user asks.

## API Key

The script checks for API key in this order:
1. `--api-key` argument (use if user provided key in chat)
2. `GEMINI_API_KEY` environment variable (also loads from `.env` / `~/.env` via python-dotenv when present)

If neither is available, the script exits with an error message.

For `--provider openrouter`, use `OPENROUTER_API_KEY` instead.

## Filename Generation

Generate filenames with the pattern: `yyyy-mm-dd-hh-mm-ss-name.png`

**Format:** `{timestamp}-{descriptive-name}.png`
- Timestamp: Current date/time in format `yyyy-mm-dd-hh-mm-ss` (24-hour format)
- Name: Descriptive lowercase text with hyphens
- Keep the descriptive part concise (1-5 words typically)
- Use context from user's prompt or conversation
- If unclear, use random identifier (e.g., `x9k2`, `a7b3`)

Examples:
- Prompt "A serene Japanese garden" → `2025-11-23-14-23-05-japanese-garden.png`
- Prompt "sunset over mountains" → `2025-11-23-15-30-12-sunset-mountains.png`
- Prompt "create an image of a robot" → `2025-11-23-16-45-33-robot.png`
- Unclear context → `2025-11-23-17-12-48-x9k2.png`

## Image Editing

When the user wants to modify an existing image:
1. Check if they provide an image path or reference an image in the current directory
2. Use `--input-image` parameter with the path to the image
3. The prompt should contain editing instructions (e.g., "make the sky more dramatic", "remove the person", "change to cartoon style")
4. Common editing tasks: add/remove elements, change style, adjust colors, blur background, etc.

## Prompt Handling

**For generation:** Pass user's image description as-is to `--prompt`. Only rework if clearly insufficient.

**For editing:** Pass editing instructions in `--prompt` (e.g., "add a rainbow in the sky", "make it look like a watercolor painting")

Preserve user's creative intent in both cases.

## Output

- Saves PNG to current directory (or specified path if filename includes directory)
- Script outputs the full path to the generated image
- **Do not read the image back** - just inform the user of the saved path

## Examples

**Generate new image (default 512):**
```bash
uv run ~/.agents/skills/nano-banana-pro/scripts/generate_image.py --prompt "A serene Japanese garden with cherry blossoms" --filename "2025-11-23-14-23-05-japanese-garden.png"
```

**Generate at higher resolution only when asked:**
```bash
uv run ~/.agents/skills/nano-banana-pro/scripts/generate_image.py --prompt "A serene Japanese garden with cherry blossoms" --filename "2025-11-23-14-23-05-japanese-garden.png" --resolution 2K
```

**Edit existing image:**
```bash
uv run ~/.agents/skills/nano-banana-pro/scripts/generate_image.py --prompt "make the sky more dramatic with storm clouds" --filename "2025-11-23-14-25-30-dramatic-sky.png" --input-image "original-photo.jpg"
```
