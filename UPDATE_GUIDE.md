# Pipedrive MCP — Update Guide

This walks you through replacing your existing Pipedrive MCP install with the
NGPF version. Works on Windows and Mac. Total time: ~5 minutes.

## Before you start

You'll need:
- `pipedrive-mcp.zip` (downloaded from Google Drive)
- Your existing install folder (wherever you extracted Pipedrive MCP the first
  time — commonly `~/PipedriveClaude/` or `Documents\PipedriveClaude\`)
- Your existing `.env` file (it stays where it is — do not delete it)

You will *not* need to:
- Update your Claude Desktop config (the install path stays the same)
- Get a new API token
- Edit `.env`
- Install anything new globally

## Step-by-step

### 1. Quit Claude Desktop completely

Closing the window isn't enough — Claude needs to fully exit so it releases
the running MCP server process.

- **Windows:** Right-click the Claude icon in the system tray (bottom-right
  corner of the screen) → **Quit**. If it's stuck, open Task Manager and
  end the Claude process.
- **Mac:** With Claude focused, press **⌘Q**, or right-click the Claude icon
  in the Dock → **Quit**. If it's stuck, open Activity Monitor and force-quit
  Claude.

### 2. Open a terminal in your install folder

- **Windows:** Open PowerShell, then `cd` into your folder:
  ```powershell
  cd ~\PipedriveClaude
  ```
- **Mac:** Open Terminal (⌘Space → "Terminal"), then `cd` into your folder:
  ```bash
  cd ~/PipedriveClaude
  ```

Run `ls` and confirm you see your existing files: `pipedrive/`, `server.py`,
`pyproject.toml`, `.env`, etc.

### 3. Archive everything except `.env`

Create an `archive/` folder and move every file and directory into it,
**except** `.env`:

- **Windows (PowerShell):**
  ```powershell
  mkdir archive
  Get-ChildItem -Force | Where-Object { $_.Name -ne '.env' -and $_.Name -ne 'archive' } | Move-Item -Destination archive
  ```

- **Mac (Terminal):**
  ```bash
  mkdir archive
  find . -mindepth 1 -maxdepth 1 ! -name '.env' ! -name 'archive' -exec mv {} archive/ \;
  ```

After this runs, only `.env` and `archive/` should remain in the folder:
- **Windows:** `ls -Force` shows `.env` and `archive/`
- **Mac:** `ls -a` shows `.`, `..`, `.env`, and `archive`

### 4. Drop in the new version

Extract `pipedrive-mcp.zip` directly into your install folder — *not* inside
`archive/`. The new files should land at the same level as `.env`.

- **Windows:** Right-click the zip in File Explorer → **Extract All...** → set
  the destination to your install folder.
- **Mac:** Double-click the zip in Finder. macOS extracts it next to the zip
  file; move the extracted contents into your install folder.

After extraction, your folder should have:
- `.env` (untouched, your existing one)
- `archive/` (your old install, kept as a safety net)
- All the new files: `pipedrive/`, `server.py`, `pyproject.toml`, `uv.lock`,
  `CLAUDE.md`, etc.

### 5. Rebuild the Python environment

Same command on both OSes:

```
uv sync
```

Takes ~20 seconds. Reinstalls dependencies into a fresh `.venv/`.

### 6. Relaunch Claude Desktop

Open Claude Desktop normally. It'll auto-launch the MCP server through your
existing config — no config changes needed because the install path is
unchanged.

- **Windows:** Click the Start menu, type "Claude", press Enter.
- **Mac:** Spotlight (⌘Space) → type "Claude" → Enter. Or open from
  Applications.

### 7. Sanity check

In a new Claude conversation, ask:

> List my Pipedrive pipelines

If pipelines come back with names you recognize, you're done. To verify the
new tools specifically:

> Show me the custom fields configured on deals
> Who are the active users in our Pipedrive
> List recent notes on deal #<some real deal id>

### 8. Delete the archive (after you've confirmed it works)

- **Windows:**
  ```powershell
  Remove-Item -Recurse -Force archive
  ```

- **Mac:**
  ```bash
  rm -rf archive
  ```

If you skip this, no harm — `archive/` just sits there. But once you're sure
everything's working, deleting it keeps the folder clean.

## Rolling back if something breaks

If the sanity check fails, your old version is intact in `archive/`.
To restore it:

- **Windows (PowerShell):**
  ```powershell
  # Remove the new files (everything except .env and archive/)
  Get-ChildItem -Force | Where-Object { $_.Name -ne '.env' -and $_.Name -ne 'archive' } | Remove-Item -Recurse -Force

  # Move the old version back
  Get-ChildItem -Path archive -Force | Move-Item -Destination .

  # Clean up the empty archive folder
  Remove-Item archive

  # Rebuild old environment
  uv sync
  ```

- **Mac (Terminal):**
  ```bash
  # Remove the new files (everything except .env and archive/)
  find . -mindepth 1 -maxdepth 1 ! -name '.env' ! -name 'archive' -exec rm -rf {} +

  # Move the old version back
  find archive -mindepth 1 -maxdepth 1 -exec mv {} . \;

  # Clean up the empty archive folder
  rmdir archive

  # Rebuild old environment
  uv sync
  ```

Then relaunch Claude Desktop. You're back to the previous working version.

## What's new in this version

This release adds 20 tools and removes 6, for a net +14 over the previous fork:

**Added:**
- **Notes** (4 tools): create, get, update, list notes attached to deals,
  people, and organizations
- **Pipelines & Stages** (5 tools, read-only): list/get pipelines and stages,
  plus list deals in a pipeline
- **Lead-to-Deal Conversion** (1 tool): `convert_lead_to_deal` runs the
  Pipedrive v2 async conversion job and returns the new deal ID
- **Custom Fields** (3 tools, read-only): inspect deal/person/org field metadata
  including custom field keys (NGPF's district, state, course type, etc.)
- **Users** (2 tools, read-only): list users, get user — resolves "Aaron's deals"
  to the right user ID without memorizing internal IDs
- **Files** (2 tools, read-only): inspect file metadata attached to entities
- **Filters** (1 tool, read-only): `list_filters` exposes saved Pipedrive
  filters so Claude can use existing saved searches instead of reconstructing
  filter logic
- **list_persons** (1 tool): plain paginated person browsing — fills a gap
  in the upstream which had create/get/update/search but no list
- **Lead-creation visibility fix**: the existing `create_lead` and 6 other
  lead tools were silently broken in the upstream fork due to missing
  `__init__.py` files; they're now wired up and visible to Claude

**Removed (still callable via the underlying API client, just not exposed as
MCP tools to Claude):**
- `delete_person_from_pipedrive`
- `delete_organization_from_pipedrive`
- `delete_deal_from_pipedrive`
- `delete_lead_from_pipedrive`
- `delete_product_from_deal`
- `delete_follower_from_organization`

This was deliberate — destructive operations are riskier and more easily
handled through Pipedrive's UI than through Claude.

## Common issues

**`uv` not found.** You're missing UV. Install it:
- **Windows:** Run `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
- **Mac:** Run `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Or follow https://docs.astral.sh/uv/getting-started/installation/

Then re-run step 5.

**Claude says "tool not available because feature is disabled"** for one of
the new modules. This means your `.env` has an explicit
`PIPEDRIVE_FEATURE_<X>=false` entry. Either remove that line or set it to
`true`. The default for every new module is enabled.

**`uv sync` fails with permission errors on `.venv/`.** Claude Desktop didn't
fully quit and is holding files open.
- **Windows:** Force-quit Claude from Task Manager, then delete `.venv/`:
  `Remove-Item -Recurse -Force .venv`. Re-run `uv sync`.
- **Mac:** Force-quit Claude from Activity Monitor, then delete `.venv/`:
  `rm -rf .venv`. Re-run `uv sync`.

**Tool count seems off.** The current version registers 51 MCP tools total.
You can verify by asking Claude "what Pipedrive tools do you have available?"
in any conversation.
