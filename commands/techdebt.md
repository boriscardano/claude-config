---
name: techdebt
description: Find and kill duplicated code and technical debt
---

Analyze the current project for technical debt:

## 1. Find Duplicate Code
- Search for similar function implementations
- Identify copy-pasted code blocks
- Look for repeated logic that could be extracted into utilities

## 2. Check for Dead Code
- Find unused imports (use ruff or similar)
- Identify unused functions/classes
- Look for commented-out code blocks

## 3. Review TODOs and FIXMEs
- List all TODO/FIXME/HACK comments with file:line
- Prioritize by apparent severity

## 4. Report Findings
Present as a prioritized list with:
- file:line references
- Brief description of the issue
- Suggested fix

## 5. Offer to Fix
For the top 3 most impactful issues, offer to refactor them now.
