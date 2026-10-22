---
type: regex
target:
  source: file
  path: docs/product/product-decisions.md
flags: m
pattern: '^- (?!✅ |❌ )'
match: not_contains
---
