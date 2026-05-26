SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS content_projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'draft',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (status IN ('draft', 'materials_ready', 'archived'))
);

CREATE TABLE IF NOT EXISTS user_materials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    material_type TEXT NOT NULL,
    title TEXT,
    text_content TEXT,
    source_url TEXT,
    stored_file_path TEXT,
    original_file_name TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES content_projects(id) ON DELETE CASCADE,
    CHECK (material_type IN ('text', 'link', 'image', 'screenshot', 'summary', 'project_record'))
);

CREATE TABLE IF NOT EXISTS topic_generation_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    provider_name TEXT NOT NULL,
    provider_version TEXT NOT NULL,
    status TEXT NOT NULL,
    requested_candidate_count INTEGER NOT NULL,
    input_material_count INTEGER NOT NULL,
    error_message TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TEXT,
    FOREIGN KEY (project_id) REFERENCES content_projects(id) ON DELETE CASCADE,
    CHECK (status IN ('running', 'succeeded', 'failed'))
);

CREATE TABLE IF NOT EXISTS topic_candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    generation_run_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    angle TEXT NOT NULL,
    audience TEXT NOT NULL,
    hook TEXT NOT NULL,
    rationale TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'candidate',
    selected_at TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES content_projects(id) ON DELETE CASCADE,
    FOREIGN KEY (generation_run_id) REFERENCES topic_generation_runs(id) ON DELETE CASCADE,
    CHECK (status IN ('candidate', 'selected', 'dismissed'))
);

CREATE TABLE IF NOT EXISTS topic_candidate_sources (
    candidate_id INTEGER NOT NULL,
    material_id INTEGER NOT NULL,
    PRIMARY KEY (candidate_id, material_id),
    FOREIGN KEY (candidate_id) REFERENCES topic_candidates(id) ON DELETE CASCADE,
    FOREIGN KEY (material_id) REFERENCES user_materials(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_content_projects_created_at
ON content_projects (created_at DESC, id DESC);

CREATE INDEX IF NOT EXISTS idx_user_materials_project_id_created_at
ON user_materials (project_id, created_at DESC, id DESC);

CREATE INDEX IF NOT EXISTS idx_topic_generation_runs_project_id_created_at
ON topic_generation_runs (project_id, created_at DESC, id DESC);

CREATE INDEX IF NOT EXISTS idx_topic_candidates_project_id_created_at
ON topic_candidates (project_id, created_at DESC, id DESC);
"""
