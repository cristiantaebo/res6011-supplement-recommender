PRAGMA foreign_keys = ON;

CREATE TABLE dataset_version (
    version_id TEXT PRIMARY KEY,
    created_date TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('draft', 'validated', 'active', 'retired')),
    source_inventory_hash TEXT NOT NULL,
    notes TEXT NOT NULL
);
CREATE UNIQUE INDEX one_active_dataset ON dataset_version(status) WHERE status = 'active';

CREATE TABLE source_record (
    source_id TEXT PRIMARY KEY,
    source_type TEXT NOT NULL CHECK (source_type IN ('academic', 'industry', 'product_page', 'synthetic')),
    title TEXT NOT NULL,
    publisher TEXT NOT NULL,
    public_url TEXT NOT NULL,
    accessed_date TEXT NOT NULL,
    synthetic INTEGER NOT NULL CHECK (synthetic IN (0, 1)),
    licence_or_use_note TEXT NOT NULL,
    evidence_path TEXT NOT NULL,
    CHECK ((source_type = 'synthetic' AND synthetic = 1) OR (source_type <> 'synthetic' AND synthetic = 0))
);

CREATE TABLE taxonomy_term (
    term_id TEXT PRIMARY KEY,
    version_id TEXT NOT NULL REFERENCES dataset_version(version_id),
    category TEXT NOT NULL CHECK (category IN ('wellness_goal', 'preference', 'format', 'dietary_label', 'boundary')),
    display_label TEXT NOT NULL,
    active INTEGER NOT NULL CHECK (active IN (0, 1))
);

CREATE TABLE term_alias (
    alias_id TEXT PRIMARY KEY,
    term_id TEXT NOT NULL REFERENCES taxonomy_term(term_id),
    normalised_phrase TEXT NOT NULL,
    priority INTEGER NOT NULL DEFAULT 0,
    UNIQUE (term_id, normalised_phrase)
);

CREATE TABLE product (
    product_id TEXT PRIMARY KEY,
    version_id TEXT NOT NULL REFERENCES dataset_version(version_id),
    display_name TEXT NOT NULL,
    predefined_summary TEXT NOT NULL,
    predefined_recommendation_text TEXT NOT NULL,
    format_id TEXT REFERENCES taxonomy_term(term_id),
    active INTEGER NOT NULL CHECK (active IN (0, 1)),
    source_id TEXT NOT NULL REFERENCES source_record(source_id)
);

CREATE TABLE recipe (
    recipe_id TEXT PRIMARY KEY,
    product_id TEXT NOT NULL REFERENCES product(product_id),
    predefined_recipe_text TEXT NOT NULL,
    source_id TEXT NOT NULL REFERENCES source_record(source_id),
    active INTEGER NOT NULL CHECK (active IN (0, 1))
);
CREATE UNIQUE INDEX one_active_recipe_per_product ON recipe(product_id) WHERE active = 1;

CREATE TABLE product_term (
    product_id TEXT NOT NULL REFERENCES product(product_id),
    term_id TEXT NOT NULL REFERENCES taxonomy_term(term_id),
    relationship TEXT NOT NULL CHECK (relationship IN ('eligible', 'matches', 'excludes')),
    source_id TEXT NOT NULL REFERENCES source_record(source_id),
    PRIMARY KEY (product_id, term_id, relationship)
);

CREATE TABLE scoring_rule (
    rule_id TEXT PRIMARY KEY,
    version_id TEXT NOT NULL REFERENCES dataset_version(version_id),
    term_id TEXT NOT NULL REFERENCES taxonomy_term(term_id),
    relationship TEXT NOT NULL CHECK (relationship IN ('eligible', 'matches')),
    weight INTEGER NOT NULL CHECK (weight BETWEEN 0 AND 10),
    predefined_reason_template TEXT NOT NULL,
    active INTEGER NOT NULL CHECK (active IN (0, 1)),
    source_id TEXT NOT NULL REFERENCES source_record(source_id),
    UNIQUE (version_id, term_id, relationship)
);

CREATE TABLE boundary_pattern (
    boundary_id TEXT PRIMARY KEY,
    normalised_phrase TEXT NOT NULL UNIQUE,
    boundary_code TEXT NOT NULL,
    predefined_response TEXT NOT NULL,
    active INTEGER NOT NULL CHECK (active IN (0, 1))
);
