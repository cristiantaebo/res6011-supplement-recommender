# Deterministic scoring worked example

Input: `mixable option vegetarian powder`  
Data/rule version: `curated-v1`

The controlled interpreter returns `goal_mixable`, `preference_vegetarian` and `format_powder`. The Myprotein record has matching stored relationships for all three.

| Rule | Controlled label | Points |
|---|---|---:|
| `crule_goal_mixable` | Mixable option | 5 |
| `crule_pref_vegetarian` | Vegetarian labelled | 3 |
| `crule_format_powder` | Powder | 2 |
| **Total** | | **10** |

No other curated product has a positive relationship for those terms. The engine therefore ranks `real_myprotein_whey_powder` first with score 10. Its name, summary, recommendation, recipe and reason fragments are retrieved from stored records; the renderer adds no product facts.

Tie oracle (synthetic fixture): equal totals sort by matched-rule count and then stable product ID. Exclusion oracle: a matched `excludes` relationship removes the product before scoring. Both are covered by `tests/test_engine.py`.
