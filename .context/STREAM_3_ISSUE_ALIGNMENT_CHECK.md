# Stream 3 Issue Alignment Check

**Date**: January 11, 2026  
**Purpose**: Verify that GitHub Issues #20-24 descriptions match Stream 3 Planning Meeting discussion  

---

## Summary

✅ **Overall Assessment**: GOOD ALIGNMENT with minor discrepancies  
**Status**: Issues are well-documented but need refinement to match meeting scope

---

## Story-by-Story Analysis

### Story 3.1: Beginner Level Curriculum (#20)

**Meeting Discussion**:
- 7 chapters: What Are AI Agents?, Environment Setup, Your First Agent, RAG Fundamentals, Tool Integration Basics, Memory & Context, Testing Your Agent
- 2 weeks effort
- No writer assigned yet (Writer A)

**Current Issue Description**:
- 6 chapters outlined: motivation, definition, problems, architecture, evolution, frameworks
- Effort: 3-4 days
- Location: `.context/curriculum/chapters/` and `.context/curriculum/slides/`

**Status**: ⚠️ **MISALIGNED**
- **Discrepancy 1**: Meeting specified 7 chapters with different content (Lab-focused), issue shows 6 chapters (theory-focused)
- **Discrepancy 2**: Meeting said 2 weeks effort, issue says 3-4 days
- **Issue**: Current description is more conceptual (motivation → frameworks), not lab-integrated as discussed

**Recommendation**: 
Update issue to:
- Change chapters to: Environment Setup, Your First Agent, RAG Fundamentals, Tool Integration Basics, Memory & Context, Testing Your Agent, Final Project
- Update effort to 2 weeks (10 days)
- Add explicit link to labs 0-2
- Clarify "lab-integrated" approach vs. pure theory

---

### Story 3.2: Intermediate Level Curriculum (#21)

**Meeting Discussion**:
- 6 chapters: Orchestrator Patterns, Advanced Memory Systems, Context Engineering, Observability & Debugging, Multi-Turn Conversations, Integration Patterns
- 2 weeks effort
- Writer B assigned (pending)

**Current Issue Description**:
- 7 chapters: orchestrator, multi_llm_routing, tools, memory_systems, context_engineering, policies_guardrails, observability
- Effort: 4-5 days
- Includes code examples and runnable snippets

**Status**: ⚠️ **MISALIGNED**
- **Discrepancy 1**: Meeting has 6 chapters, issue has 7 (added "multi_llm_routing" and "policies_guardrails")
- **Discrepancy 2**: Meeting said 2 weeks, issue says 4-5 days (half the time)
- **Extra Content**: Issue includes "policies_guardrails" which should be in Advanced (Story 3.3)

**Recommendation**:
Update issue to:
- Remove "i02_multi_llm_routing" and "i06_policies_guardrails" (move to Advanced)
- Adjust chapters to: Orchestrator Patterns, Advanced Memory Systems, Context Engineering, Observability & Debugging, Multi-Turn Conversations, Integration Patterns
- Update effort to 2 weeks (10 days)
- Keep code examples (good addition to meeting scope)

---

### Story 3.3: Advanced Level Curriculum (#22)

**Meeting Discussion**:
- 6 chapters: Safety & Guardrails, Multi-Agent Systems, Production Deployment, Scaling Strategies, Monitoring & Alerting, Security Best Practices
- 2 weeks effort
- Writer C assigned (pending)

**Current Issue Description**:
- 6 chapters: design_decisions, failure_modes, testing_evaluation, security, human_in_loop, scalability
- Effort: 5-6 days
- Includes case studies and ADRs

**Status**: ⚠️ **SIGNIFICANTLY MISALIGNED**
- **Discrepancy 1**: Current chapters don't match meeting discussion at all
  - Current: design_decisions, failure_modes, testing_evaluation, security, human_in_loop, scalability
  - Meeting: Safety & Guardrails, Multi-Agent Systems, Production Deployment, Scaling Strategies, Monitoring & Alerting, Security Best Practices
- **Discrepancy 2**: Meeting said 2 weeks, issue says 5-6 days (one-third the time)
- **Issue**: Current description is more architectural/design-focused, not production-deployment focused

**Recommendation**:
Update issue to align with meeting:
- Change chapters to: Safety & Guardrails, Multi-Agent Systems, Production Deployment, Scaling Strategies, Monitoring & Alerting, Security Best Practices
- Update effort to 2 weeks (10 days)
- Add explicit docker/kubernetes references for production deployment
- Keep case study and ADR approach (good addition)

---

### Story 3.4: Pro Level Curriculum (#23)

**Meeting Discussion**:
- 4 chapters: Advanced Agent Frameworks, Agent Research & Innovations, Custom Tool Development, Contributing to Agent Ecosystems
- 1.5 weeks effort
- Writer D assigned (pending)

**Current Issue Description**:
- 6 chapters: customer_support_agents, coding_agents, medical_agents, ops_agents, deployment_models, future_directions
- Effort: 6-7 days
- Domain-specific deep dives

**Status**: ⚠️ **SIGNIFICANTLY MISALIGNED**
- **Discrepancy 1**: Current is domain-specific (support, coding, medical, ops), meeting is framework/research focused
- **Discrepancy 2**: Current has 6 chapters, meeting has 4 chapters
- **Issue**: Current approach looks like "domain applications" which should be in Supporting Materials or separate stream

**Recommendation**:
Update issue to align with meeting:
- Change to 4 chapters: Advanced Agent Frameworks, Agent Research & Innovations, Custom Tool Development, Contributing to Agent Ecosystems
- Update effort to 1.5 weeks (7 days)
- Focus on LangGraph, frameworks, research papers, open source contributions
- Move domain-specific content (support, medical, ops) to Story 3.5 as case studies

---

### Story 3.5: Supporting Materials (#24)

**Meeting Discussion**:
- 2 chapters: Case Studies (5 real-world implementations), Quick Reference Guide
- Additional resources: Glossary, API Reference, Video Tutorials (15 total), Assessment Quizzes (25 per level), Certificate Program
- 1.5 weeks effort
- Writer E assigned (pending)

**Current Issue Description**:
- 6 components: Glossary (50+ terms), Project Templates (12), Learner Workbooks (4), Quick Reference, Links Index, Assessment Rubrics
- Effort: 3-4 days
- Includes templates in Idea format

**Status**: ⚠️ **PARTIALLY ALIGNED**
- **Good Alignment**:
  - Both include Glossary ✓
  - Both include Quick Reference ✓
  - Both include Assessment materials ✓
- **Discrepancy 1**: Current has "Project Templates" and "Workbooks" (not in meeting discussion)
- **Discrepancy 2**: Meeting emphasized "Case Studies" (5 implementations), current doesn't highlight
- **Discrepancy 3**: Meeting mentioned "Video Tutorials" (15), current doesn't include
- **Discrepancy 4**: Meeting mentioned "Certificate Program", current doesn't include
- **Effort**: Both around 3-4 days, but current omits video production

**Recommendation**:
Update issue to include meeting scope:
- Add explicit Case Studies section (5 implementations: Customer Support, Research Assistant, DevOps, Trading, Healthcare)
- Add Video Tutorials section (15 videos, 5-10 min each)
- Add Certificate Program section
- Keep Glossary, Quick Reference, Assessment materials
- Decide on: keep/remove Project Templates and Workbooks (might be good additions not discussed)
- Adjust effort to 1.5-2 weeks to account for video production

---

## Root Cause Analysis

Why are there discrepancies?

1. **Timing**: Issues were likely created before the Stream 3 planning meeting (meeting was Jan 11 @ 6 PM)
2. **Source**: Issues appear to reference earlier curriculum design docs, not the meeting decisions
3. **Scope Creep**: Some issues (3.1, 3.2, 3.3) have slightly expanded scope beyond meeting discussion
4. **Missing Items**: Supporting Materials (#24) is missing video production and certificate program

---

## Alignment Matrix

| Issue | Meeting Scope | Current Scope | Match % | Action |
|-------|---------------|---------------|---------|--------|
| #20 - Beginner | 7 chapters (lab-focused) | 6 chapters (theory-focused) | 60% | 🔴 UPDATE |
| #21 - Intermediate | 6 chapters + code | 7 chapters + code | 80% | 🟡 REFINE |
| #22 - Advanced | 6 chapters (production-focused) | 6 chapters (design-focused) | 40% | 🔴 UPDATE |
| #23 - Pro | 4 chapters (frameworks) | 6 chapters (domains) | 30% | 🔴 UPDATE |
| #24 - Supporting | Cases + Glossary + Videos | Templates + Glossary | 70% | 🟡 REFINE |

---

## Recommended Action Plan

### CRITICAL (Update Immediately)

**Story 3.1 (#20)**: 
- Update chapters to match meeting (7 chapters, lab-integrated)
- Change effort to 2 weeks
- Add Writer A assignment

**Story 3.3 (#22)**:
- Complete rewrite to focus on production deployment, scaling, monitoring
- Change effort to 2 weeks
- Add Writer C assignment

**Story 3.4 (#23)**:
- Change from domain-specific to frameworks/research
- Reduce chapters from 6 to 4
- Update effort to 1.5 weeks
- Add Writer D assignment

### IMPORTANT (Refine for Accuracy)

**Story 3.2 (#21)**:
- Remove "policies_guardrails" chapter (move to 3.3)
- Clarify effort is 2 weeks, not 4-5 days
- Add Writer B assignment

**Story 3.5 (#24)**:
- Add Case Studies section (5 implementations)
- Add Video Tutorials section (15 videos)
- Add Certificate Program section
- Update effort to 1.5-2 weeks
- Add Writer E assignment

---

## Next Steps

1. **PM Action**: Update all 5 issue descriptions to align with meeting scope
2. **PM Action**: Assign Writers A-E to respective stories
3. **PO Action**: Review updated descriptions for final approval
4. **Architect Action**: Review for technical accuracy after updates

**Timeline**: Complete by COB Jan 13, 2026 (allow writers 2 days to prepare before Week 9 kickoff)

---

**Document Created**: January 11, 2026 @ 19:45 IST  
**Status**: ALIGNMENT CHECK COMPLETE - ACTION ITEMS IDENTIFIED

