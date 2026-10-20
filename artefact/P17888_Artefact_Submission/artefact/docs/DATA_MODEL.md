# Controlled data model (I-02)

`dataset_version` owns versioned taxonomy terms, products and scoring rules. `source_record` supplies explicit provenance; `term_alias` maps controlled phrases to taxonomy terms, with deliberate duplicate phrases for ambiguity tests. `product_term` records source-backed matches, exclusions or eligibility. Each active `scoring_rule` has a stable ID, taxonomy term, relationship, bounded integer weight, predefined reason, version and source. `recipe` preserves the authorised terminology using predefined text only. `boundary_pattern` contains predefined boundary codes and responses.

All content rows carry a source relationship, one partial unique index permits exactly one active dataset, foreign keys are enabled during construction and access is read-only at runtime. The committed seed is explicitly synthetic and neutral; generated SQLite files are excluded from Git.

```mermaid
erDiagram
  dataset_version ||--o{ taxonomy_term : contains
  dataset_version ||--o{ product : contains
  dataset_version ||--o{ scoring_rule : versions
  source_record ||--o{ product : supports
  source_record ||--o{ recipe : supports
  source_record ||--o{ product_term : supports
  source_record ||--o{ scoring_rule : supports
  taxonomy_term ||--o{ term_alias : has
  taxonomy_term ||--o{ product_term : classifies
  taxonomy_term ||--o{ scoring_rule : weights
  product ||--o{ product_term : has
  product ||--o{ recipe : has
```
