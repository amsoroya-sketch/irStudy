# Constraints Folder - Modular Constraint System

**Created**: 2026-01-26
**Purpose**: Break down large PROJECT_CONSTRAINTS.md into manageable modules
**Structure**: One file per major constraint category

---

## Why Modular Structure?

**Problem**: Original `PROJECT_CONSTRAINTS.md` was 30,000+ tokens
- Too large to read completely
- Difficult to navigate
- Hard to maintain
- Agents couldn't read it all before starting work

**Solution**: Split into topic-specific modules
- Easier to read (each file 2000-5000 tokens)
- Better navigation (read only what you need)
- Simpler maintenance (update specific sections)
- Agents can read relevant constraints quickly

---

## File Structure

```
constraints/
├── README.md (this file)
├── 4-llm-integration.md (✅ CREATED 2026-01-26)
└── (other constraint files - to be created)
```

### Created Files

#### 4-llm-integration.md (✅ 2026-01-26)
**Size**: ~5000 tokens (manageable)
**Sections**:
- 4.0: Python Environment & LLM Requirements
- 4.1: Ollama Client Usage
- 4.2: LLM Capabilities for Complex Medical Content (NEW - CRITICAL)

**Why created first**: Just added Section 4.2 documenting that local 7B models cannot generate complex MCQs.

---

## How to Use

### For Agents

**Before starting work**:
1. Identify your task type (MCQ generation? Testing? Security?)
2. Read relevant constraint file from this folder
3. Follow implementation checklist in constraint file
4. Validate work against constraints before returning

**If constraint file doesn't exist yet**:
- Read legacy `PROJECT_CONSTRAINTS.md`
- Extract relevant section

---

## Benefits

✅ Read only relevant constraints (faster)
✅ Easier to maintain and update
✅ Clear implementation checklists
✅ Better documentation organization

---

**Status**: ✅ ACTIVE (v3.0.0 Modular Structure)
