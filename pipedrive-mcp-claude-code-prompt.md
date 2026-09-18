# Pipedrive MCP Fork: Build Spec for Claude Code

## Context

You are working in a fork of `Wirasm/pipedrive-mcp`. The fork is hosted at:

```
https://github.com/davidpm1021/pipedrive-mcp
```

The fork is being adapted for NGPF (Next Gen Personal Finance) so the partnerships team can run their Pipedrive workflow through Claude Desktop. The full architectural plan is documented in this Notion page, which is the canonical source of truth for what to build:

https://www.notion.so/3348b47b65be8127867de4d1db1389bc

This file supplements that spec with build-time guidance, commit boundaries, and known landmines.

---

## Pre-Flight Check

Before writing any code, confirm the following from the working directory `D:\Cursor Projects\pipedrive-mcp`:

1. `git status` shows a clean working tree on `main`.
2. `git remote -v` shows `origin` pointing to the personal fork (not Wirasm directly).
3. `uv` is installed and `uv sync` completes successfully.
4. The Pipedrive API token is available in `.env` (or wherever the upstream expects it). Verify by running the server once and listing the existing tools.
5. Note the actual upstream tool count from `uv run server.py` output. The Notion spec quotes "30" in one place and "33 after delete removal" in another, which is internally inconsistent. Use the live server output as the source of truth, not the documented numbers.

If any of the above fails, stop and report. Do not start the build with a broken environment.

---

## Cross-Cutting Rules

These apply to every phase below.

### 1. Ask, don't guess

When the upstream codebase has an architectural ambiguity (where should the v2 API client live, how should new feature flags be registered, what's the right pattern for async polling), pause and ask before making the call. Pattern-matching to the wrong existing module is the single most expensive failure mode here. A 30-second clarifying question beats an hour of refactoring.

### 2. Test coverage is required for new modules

The upstream test suite covers the existing modules. Each new module you add must include at least one happy-path integration test per tool, with the Pipedrive API mocked. Without this, regressions in future updates will be invisible until production. The bar is "the test would catch an obvious break," not "exhaustive coverage."

### 3. v1 vs v2 API awareness

All upstream modules use the Pipedrive v1 API and are synchronous. Phase 2C (lead-to-deal conversion) is the exception. It uses the v2 API and is asynchronous. See Phase 2C below for the specific shape. Do not pattern-match v2 endpoints onto v1 client conventions.

### 4. Commit boundaries

Each phase below ends with a single commit. Do not bundle multiple phases into one commit. The phases are designed to be bisectable. Use the exact commit message provided.

### 5. Feature flags

Every new module gets a feature flag in `feature_config.py` (or wherever flags live in the upstream), defaulting to `true`. This lets the partnerships team selectively disable a module if something goes wrong post-rollout, without rolling back the whole release.

### 6. Tool count tracking

After each phase, restart the server and verify the new tool count by listing tools. The Notion spec's absolute counts may be off; what matters is the delta. Phase 1 should remove 6. Each Phase 2 sub-phase should add the number indicated below.

---

## Phase 1: Remove Destructive Tool Definitions

Remove the MCP tool registrations for these six deletes. Keep the underlying API client methods (in `client/`) so they can be revived later if needed; only strip the tool registration layer.

- `delete_person_from_pipedrive`
- `delete_organization_from_pipedrive`
- `delete_deal_from_pipedrive`
- `delete_lead_from_pipedrive`
- `delete_product_from_deal`
- `delete_follower_from_organization`

**Exit criteria:**
- `uv run pytest` passes (some upstream tests may need to be skipped or updated if they exercised the delete tools at the MCP layer).
- Server starts cleanly.
- Tool count is 6 fewer than the baseline noted in pre-flight.
- No references to the removed tool names remain in tool registration code (a `grep` should come back empty).

**Commit:** `Remove destructive tools from MCP surface (6 tools)`

---

## Phase 2A: Notes Module

Add Create, Get, Update, List operations for notes attached to deals, people, and organizations. No delete.

Follow the upstream vertical slice pattern: a `client/`, `models/`, and `tools/` directory per feature. Mirror how Activities or Deals are structured, since those are the closest analogs.

Tools (4 total):
- `create_note`
- `get_note`
- `update_note`
- `list_notes` (filterable by deal_id, person_id, org_id)

**Exit criteria:**
- 4 new tools registered.
- Each tool has a happy-path integration test with mocked Pipedrive responses.
- Feature flag added to `feature_config.py`, defaulting to `true`.
- Tool count increased by 4 from end of Phase 1.

**Commit:** `Add notes module (4 tools, CRU)`

---

## Phase 2B: Pipelines and Stages Module (Read-Only)

Tools (5 total):
- `list_pipelines`
- `get_pipeline`
- `list_stages` (filterable by pipeline_id)
- `get_stage`
- `list_deals_in_pipeline`

This is the module that makes "advance the Lenape Public Schools deal" actually work. Without it, Claude has no way to know what stages exist in NGPF's pipeline.

**Exit criteria:**
- 5 new tools registered.
- Integration tests for each.
- Feature flag added.
- Tool count increased by 5 from end of Phase 2A.

**Commit:** `Add pipelines and stages module (5 tools, read-only)`

---

## Phase 2C: Lead-to-Deal Conversion (v2 API, Async)

**Read this whole section before starting.**

Endpoint: `POST /api/v2/leads/{id}/convertToDeal`

Behavior:
- Returns `202 Accepted` with a `conversion_status_url` (or similar field, verify against current Pipedrive docs).
- The conversion runs asynchronously on Pipedrive's side.
- Poll the status URL until status is `completed` or `failed`. On `completed`, the response includes the new `deal_id`.
- On `failed`, surface the error to the caller.

Tool (1 total):
- `convert_lead_to_deal`

Implementation notes:
- If the upstream codebase has no v2 API client infrastructure, you'll need to add one. Pause and ask before scaffolding a parallel client; the user may want a specific layout.
- Set a reasonable polling timeout (suggest 30 seconds with 1-second intervals as a starting point, but ask if unclear).
- The tool's response should include the new `deal_id` on success and a clear error message on failure.

**Exit criteria:**
- 1 new tool registered.
- Integration test mocks the 202 response, mocks the polling sequence (status: pending, pending, completed), and verifies the returned `deal_id`.
- Second integration test mocks a `failed` status and verifies the error is surfaced.
- Feature flag added.
- Tool count increased by 1 from end of Phase 2B.

**Commit:** `Add lead-to-deal conversion module (1 tool, v2 async)`

---

## Phase 2D: Custom Fields Module (Read-Only)

Tools (3 total):
- `list_deal_fields`
- `list_person_fields`
- `list_org_fields`

Why this matters: NGPF has custom fields on deals (district, state, course type, etc.). Without these tools, Claude can't see what custom fields exist when creating or updating records, so it'll either omit them or hallucinate field names.

**Exit criteria:**
- 3 new tools registered.
- Integration tests for each.
- Feature flag added.
- Tool count increased by 3 from end of Phase 2C.

**Commit:** `Add custom fields module (3 tools, read-only)`

---

## Phase 2E: Users Module (Read-Only)

Tools (2 total):
- `list_users`
- `get_user`

Resolves "show me Aaron's deals" to the correct user ID without requiring the team to memorize Pipedrive's internal IDs.

**Exit criteria:**
- 2 new tools registered.
- Integration tests for each.
- Feature flag added.
- Tool count increased by 2 from end of Phase 2D.

**Commit:** `Add users module (2 tools, read-only)`

---

## Phase 2F: Files Module (Read-Only)

Tools (2 total):
- `list_files` (filterable by deal_id, person_id, org_id)
- `get_file_metadata`

Read-only for v1. File upload (POST) can be added later if the partnerships team needs it.

**Exit criteria:**
- 2 new tools registered.
- Integration tests for each.
- Feature flag added.
- Tool count increased by 2 from end of Phase 2E.

**Commit:** `Add files module (2 tools, read-only)`

---

## Final Smoke Test

After all phases are committed:

1. `git log --oneline` should show 7 new commits beyond the fork point (one per phase).
2. `uv run pytest` passes.
3. Server starts cleanly with no errors.
4. Listed tools should be: baseline minus 6 plus 17 = baseline plus 11 net. Verify the absolute count matches expectations once you confirm the baseline.
5. Manually exercise one tool from each new module against the live Pipedrive instance (e.g., `list_pipelines`, `list_users`, `list_deal_fields`) to confirm real API responses work, not just mocked ones.
6. Update `README.md` with the new tool list and a brief NGPF-specific section explaining the fork's purpose.
7. Update `CHANGELOG.md` (create if missing) noting:
   - Removed: 6 destructive tools
   - Added: 6 new modules (17 tools)
   - Source: forked from Wirasm/pipedrive-mcp at commit `<sha>`
8. Push to origin.

---

## Post-Build Handoff (Out of Scope for Claude Code)

Once the build is done, the user will:

1. Update the Notion rollout doc (`https://www.notion.so/3348b47b65be8127867de4d1db1389bc`) with the actual fork URL.
2. Walk Aaron through the migration from upstream Wirasm:
   ```
   cd ~/PipedriveClaude
   git remote set-url origin https://github.com/davidpm1021/pipedrive-mcp.git
   git pull
   uv sync
   ```
3. Restart Claude Desktop.
4. Roll out to the rest of the partnerships team.

Do not perform these steps as part of the build. The build ends when the final commit is pushed.
