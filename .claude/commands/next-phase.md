---
description: Transition to next development phase with validation
allowed-tools: Read, Write, Bash(git status), Bash(git log --oneline -10)
---

# Next Phase Transition

You are managing the transition from the current phase to the next phase in the development plan.

## Your Task
1. **Validate current phase completion** against all acceptance criteria
2. **Generate phase completion report** summarizing what was accomplished
3. **Check prerequisites** for the next phase
4. **Prepare next phase briefing** with scope and objectives
5. **Request explicit approval** before proceeding
6. **STOP and WAIT** for human confirmation

## Phase Transition Process

### Step 1: Current Phase Validation
#### ✅ Phase Completion Checklist
Review and verify:
- [ ] All deliverables completed and tested
- [ ] All acceptance criteria met
- [ ] Code committed and builds successfully
- [ ] Tests passing (unit, integration, manual)
- [ ] Documentation updated
- [ ] No critical issues or blockers remaining

#### 📋 Phase Completion Report
**Phase [N] Summary:**
- **Goal Achieved:** [Yes/No with explanation]
- **Deliverables:** [List completed items]
- **Quality Gates:** [All tests/reviews passed]
- **Key Accomplishments:** [What was built]
- **Lessons Learned:** [What we discovered]
- **Remaining Technical Debt:** [Any shortcuts taken]

### Step 2: Next Phase Preparation
#### 🎯 Phase [N+1] Overview
- **Phase Name:** [Next phase name]
- **Objective:** [What this phase will accomplish]
- **Duration Estimate:** [Expected timeline]
- **Key Deliverables:** [Main outputs]
- **Success Criteria:** [How we'll know it's done]

#### ⚠️ Prerequisites Check
- ✅ Previous phase fully complete
- ✅ Dependencies resolved
- ✅ Resources available
- ✅ Technical requirements met

### Step 3: Approval Request
**🚨 APPROVAL REQUIRED 🚨**

Before proceeding to Phase [N+1], I need explicit confirmation that the prior phase has been completed.
   
**⏸️ STOPPING POINT**
I will wait for your explicit approval before starting any Phase [N+1] work.

## Instructions
1. Read the build plan to understand current and next phases
2. Thoroughly validate current phase completion
3. Prepare comprehensive transition briefing
4. Request specific approvals
5. DO NOT start next phase work without explicit confirmation
6. If any validation fails, report issues and recommendations

## Response Options
After running this command, respond with:
- **"APPROVED - Proceed to Phase [N+1]"** - Start next phase
- **"HOLD - Need changes"** - Address issues first
- **"MODIFY - [specific changes]"** - Adjust scope/plan

Please validate current phase and prepare next phase transition.