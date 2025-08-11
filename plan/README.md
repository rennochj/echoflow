# EchoFlow Build Plans

## Current Plan
- **echoflow.plan.md** - The active, current build plan for EchoFlow development (required naming per .claude/commands/create-plan.md)

## Archived Plans
All previous versions are stored in the `/archive/` directory:

- `echoflow-v2.0-archived.md` - Initial 6-week build plan
- `echoflow-v2.1-archived.md` - Post Phase 1 implementation plan  
- `echoflow-v3.0-archived.md` - Comprehensive build plan v3.0

## Plan Versioning Guidelines

### For Future Updates:
1. **Current Plan**: Always use `echoflow.plan.md` as the active plan (per .claude/commands/create-plan.md requirement)
2. **Versioning**: When making major updates, archive the current plan first:
   ```bash
   mv echoflow.plan.md archive/echoflow-v{NEW_VERSION}-archived.md
   ```
3. **Single Source of Truth**: Only one active build plan should exist at any time

### Plan Update Process:
1. Archive current plan with version number
2. Create new `echoflow.plan.md` with updated content
3. Update this README if needed
4. Never have multiple active plans simultaneously

This structure ensures clarity and prevents confusion about which plan is current.