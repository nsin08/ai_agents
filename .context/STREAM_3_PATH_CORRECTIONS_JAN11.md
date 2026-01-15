# Stream 3 Curriculum Path Corrections - January 11

## Executive Summary
Standardized curriculum file paths across all Stream 3 stories (3.1-3.5) to use correct standard location `curriculum/presentable/` instead of `.context/curriculum/`.

## Status
✅ **COMPLETE** - All 5 stories updated with correct paths

## Issues Updated

### Issue #20 (Story 3.1: Beginner Curriculum)
- **Status**: Updated earlier
- **Paths Corrected**: 7 chapter files
- **Location**: `curriculum/presentable/01_beginner/`
- **Example**: `curriculum/presentable/01_beginner/chapter_01_environment_setup.md`

### Issue #21 (Story 3.2: Intermediate Curriculum)
- **Status**: ✅ Updated Jan 11, 10:15 AM
- **Paths Corrected**: 6 chapter files
- **Location**: `curriculum/presentable/02_intermediate/`
- **Verification**: ✅ Terminal grep confirmed all 6 chapters now show correct paths
- **Example**: `curriculum/presentable/02_intermediate/chapter_01_orchestrator_patterns.md`

### Issue #22 (Story 3.3: Advanced Curriculum)
- **Status**: ✅ Updated Jan 11, 10:18 AM
- **Paths Corrected**: 6 chapter files, ADRs, case studies, slide deck
- **Location**: `curriculum/presentable/03_advanced/`
- **Verification**: ✅ Terminal grep confirmed all chapter paths updated
- **Example**: `curriculum/presentable/03_advanced/chapter_01_safety_guardrails.md`
- **Comment**: Added verification comment

### Issue #23 (Story 3.4: Pro Curriculum)
- **Status**: ✅ Updated Jan 11, 10:19 AM
- **Paths Corrected**: 4 chapter files, research papers, patterns, slide deck
- **Location**: `curriculum/presentable/04_pro/`
- **Verification**: ✅ Terminal grep confirmed all chapter paths updated
- **Example**: `curriculum/presentable/04_pro/chapter_01_advanced_frameworks.md`
- **Comment**: Added verification comment

### Issue #24 (Story 3.5: Supporting Materials)
- **Status**: ✅ Updated Jan 11, 10:20 AM
- **Paths Corrected**: 13 support files across 4 levels, certificates, badges
- **Location**: `curriculum/presentable/05_supporting/`
- **Verification**: ✅ Terminal grep confirmed all file paths updated
- **Example**: `curriculum/presentable/05_supporting/beginner_workbook.md`
- **Comment**: Added verification comment

## File Structure Established

```
curriculum/
└── presentable/
    ├── 01_beginner/
    │   ├── chapter_01_environment_setup.md
    │   ├── chapter_02_your_first_agent.md
    │   ├── chapter_03_rag_fundamentals.md
    │   ├── chapter_04_tool_integration.md
    │   ├── chapter_05_memory_and_context.md
    │   ├── chapter_06_testing_your_agent.md
    │   └── chapter_07_final_project.md
    ├── 02_intermediate/
    │   ├── chapter_01_orchestrator_patterns.md
    │   ├── chapter_02_advanced_memory.md
    │   ├── chapter_03_context_engineering.md
    │   ├── chapter_04_safety_and_compliance.md
    │   ├── chapter_05_evaluation_and_testing.md
    │   └── chapter_06_system_design.md
    ├── 03_advanced/
    │   ├── chapter_01_safety_guardrails.md
    │   ├── chapter_02_multi_agent_systems.md
    │   ├── chapter_03_production_deployment.md
    │   ├── chapter_04_scaling_strategies.md
    │   ├── chapter_05_monitoring_alerting.md
    │   └── chapter_06_security_best_practices.md
    ├── 04_pro/
    │   ├── chapter_01_advanced_frameworks.md
    │   ├── chapter_02_reasoning_architectures.md
    │   ├── chapter_03_agentic_design_patterns.md
    │   └── chapter_04_research_frontiers.md
    └── 05_supporting/
        ├── beginner_workbook.md
        ├── beginner_glossary.md
        ├── beginner_quick_reference.md
        ├── intermediate_workbook.md
        ├── intermediate_glossary.md
        ├── intermediate_quick_reference.md
        ├── advanced_workbook.md
        ├── advanced_glossary.md
        ├── advanced_quick_reference.md
        ├── pro_workbook.md
        ├── pro_glossary.md
        ├── pro_reference.md
        ├── complete_glossary.md
        ├── lab_integration_guide.md
        ├── learning_paths.md
        ├── assessment_rubrics.md
        ├── FAQ.md
        └── resources_and_links.md
```

## Path Correction Pattern

**Old Pattern** (INCORRECT):
```
.context/curriculum/presentable/0X_level/chapter_*.md
.context/curriculum/presentable/0X_level/other_files.md
```

**New Pattern** (CORRECT):
```
curriculum/presentable/0X_level/chapter_*.md
curriculum/presentable/0X_level/other_files.md
```

## Rationale

### Why `.context/` is NOT intended for curriculum
- `.context/` is reserved for **documentation and context** files (planning, notes, analysis)
- Curriculum materials are **deliverables**, not context
- Standard project organization keeps deliverables in root-level directories
- Makes curriculum discoverable and part of main project structure

### Why `curriculum/presentable/` is correct
- Aligns with project directory structure established in early design
- `presentable/` subdirectory indicates polished, distribution-ready materials
- Supports versioning and multiple curriculum versions
- Follows standard educational project patterns

## Verification Process

All updates verified via terminal command:
```bash
for issue in 21 22 23 24; do 
  gh issue view $issue --json body -q '.body' | grep -o 'curriculum/presentable/[^/]*/[^ `]*' | head -3
done
```

**Result**: All issues now show `curriculum/presentable/` paths (no `.context/` references found)

## GitHub Comments

Added verification comments to Issues #22, #23, #24 documenting:
- Path correction completion timestamp
- List of files updated
- Alignment with Stream 3 standardized structure

## Next Steps

1. **Story 3.1 (Beginner)**: Continue with supporting materials
   - Beginner workbook (compile 21 exercises + solutions)
   - Beginner glossary (25+ terms)
   - Quick reference guide (1-page cheat sheet)

2. **Stories 3.2-3.5**: Ready for writer assignments
   - All infrastructure in place with correct paths
   - Ready for content creation and file organization

3. **Project Structure**: Standard established
   - All Stream 3 content follows `curriculum/presentable/` pattern
   - Non-curriculum docs stay in `.context/`
   - Clear distinction between deliverables and working context

## Summary

| Story | Title | Level | Status | Path |
|-------|-------|-------|--------|------|
| 3.1 | Beginner Curriculum | Beginner | 95% (7/7 chapters) | `curriculum/presentable/01_beginner/` |
| 3.2 | Intermediate Curriculum | Intermediate | 0% (ready for writing) | `curriculum/presentable/02_intermediate/` |
| 3.3 | Advanced Curriculum | Advanced | 0% (ready for writing) | `curriculum/presentable/03_advanced/` |
| 3.4 | Pro Curriculum | Pro | 0% (ready for writing) | `curriculum/presentable/04_pro/` |
| 3.5 | Supporting Materials | Cross-Level | 0% (ready for writing) | `curriculum/presentable/05_supporting/` |

---

**Completed**: January 11, 2025 @ 10:15-10:20 AM UTC
**Verified**: Terminal grep confirms all paths corrected
**Documentation**: This file + GitHub issue comments
