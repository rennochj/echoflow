---
description: Analyze PRD and create phased development plan
allowed-tools: Read, Write
---

# Build Plan Generator

You are an expert solution architect helping to create or update a phased development plan.

## Your Task
1. **Read and analyze** the CLAUDE.md file to understand:
   - Project coding standards
   - Architecture preferences  
   - Development guidelines
   - Quality requirements

2. **Read and analyze** the PRD document to understand:
   - Product scope and features
   - Success metrics
   - Timeline constraints
   - Technical requirements

3. **Create a structured build plan** that breaks the work into logical phases

## Build Plan Requirements
- Each phase should be **independently deliverable**
- Phases should **build incrementally** toward the final product
- Each phase should include **detailed implementation steps**
- Include **clear acceptance criteria** for each phase
- Identify **dependencies** between phases
- Include **testing and validation** steps
- Include indicators to **measure progress and success of phases and steps**

## Output Format
Use the standard Build Plan Template format with:
- Phase breakdown with clear scope boundaries
- Acceptance criteria for each phase
- Risk assessment per phase
- Recommended phase sequence
- Stopping points for review and approval
- Progress indicators for each phase and tasks or steps

Please analyze @CLAUDE.md and the latest PRD document in the /requirements directory (find the highest version number, e.g. v3 is newer than v1) and create a comprehensive build plan.

After creating the plan, STOP and wait for approval before proceeding with Phase 1 implementation.