# Public-secondary source curation — I-07

Version: `curated-v1`  
Access/review date: 2026-08-08  
Inventory SHA-256: `1cd009f4faaa67efbe1841fa3b41e3fac374130eaac471d7afcbd02605e6c81b`

## Selection method

Only official public product pages were used. The dataset keeps a product name, explicit dosage form, explicit vegetarian/gluten-free label where present, and public suggested-use wording. Marketing, price, popularity, efficacy, disease, diagnosis, treatment, safety and suitability statements were deliberately excluded. The prototype's matching sentence is a project-authored boundary statement, not a source efficacy claim.

| Product/source | Fields admitted | Fields rejected |
|---|---|---|
| [Myprotein Impact Whey Protein Powder](https://www.myprotein.com/p/sports-nutrition/impact-whey-protein-powder/10530943/) | Name; ready-to-mix powder; vegetarian label; public mixing directions | Performance/recovery/muscle/health claims, price, reviews, popularity and availability |
| [Solgar Gelatin Capsules](https://www.solgar.com/products/solgar-gelatin-capsules) | Name; capsule form; gluten-free label; public suggested use | Quality/manufacturing marketing and any implied safety/suitability conclusion |
| [Centrum MultiGummies Multi + Antioxidants](https://www.centrum.com/content/cf-consumer-healthcare/bp-wellness-centrum/en_US/home/products-version-b/Women/centrum-multigummies-multi-antioxidants.html) | Name; gummy form; gluten-free label; public suggested use | Immune/brain/vitality/cellular/antioxidant-effect claims, gender targeting and marketing |

## Source-to-field map

Each `product.source_id`, `recipe.source_id` and `product_term.source_id` resolves to the official page that supports the admitted field. Scoring weights/reason templates resolve to `source_project_method`, explicitly marked synthetic/project-owned. Taxonomy terms describe non-medical form or label choices and do not represent health conditions or clinical goals.

## Version separation and rollback

- `seed.synthetic.json` remains the immutable regression fixture and is never promoted as real content.
- `seed.curated.json` is the default local demonstration dataset.
- Generated SQLite files remain ignored and are rebuilt from the selected seed.
- Rollback is deterministic: restore `DEFAULT_SEED_PATH` to the validated synthetic seed or select the prior Git tag; no runtime/user data needs migration.

## Limitations

This is a deliberately small demonstration sample of three products. Public pages can change after the recorded access date. The prototype does not assess individual needs, interactions, contraindications, safety, effectiveness or suitability and does not replace the current label or professional advice.
