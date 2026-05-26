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

CREATE TABLE IF NOT EXISTS script_generation_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    selected_topic_candidate_id INTEGER NOT NULL,
    provider_name TEXT NOT NULL,
    provider_version TEXT NOT NULL,
    status TEXT NOT NULL,
    requested_script_count INTEGER NOT NULL,
    input_material_count INTEGER NOT NULL,
    error_message TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TEXT,
    FOREIGN KEY (project_id) REFERENCES content_projects(id) ON DELETE CASCADE,
    FOREIGN KEY (selected_topic_candidate_id) REFERENCES topic_candidates(id) ON DELETE CASCADE,
    CHECK (status IN ('running', 'succeeded', 'failed'))
);

CREATE TABLE IF NOT EXISTS script_drafts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    generation_run_id INTEGER NOT NULL,
    topic_candidate_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    opening_hook TEXT NOT NULL,
    body TEXT NOT NULL,
    call_to_action TEXT NOT NULL,
    estimated_duration_seconds INTEGER NOT NULL,
    rationale TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft',
    selected_at TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES content_projects(id) ON DELETE CASCADE,
    FOREIGN KEY (generation_run_id) REFERENCES script_generation_runs(id) ON DELETE CASCADE,
    FOREIGN KEY (topic_candidate_id) REFERENCES topic_candidates(id) ON DELETE CASCADE,
    CHECK (status IN ('draft', 'selected', 'dismissed'))
);

CREATE TABLE IF NOT EXISTS script_draft_sources (
    script_draft_id INTEGER NOT NULL,
    material_id INTEGER NOT NULL,
    PRIMARY KEY (script_draft_id, material_id),
    FOREIGN KEY (script_draft_id) REFERENCES script_drafts(id) ON DELETE CASCADE,
    FOREIGN KEY (material_id) REFERENCES user_materials(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS storyboard_generation_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    selected_topic_candidate_id INTEGER NOT NULL,
    selected_script_draft_id INTEGER NOT NULL,
    provider_name TEXT NOT NULL,
    provider_version TEXT NOT NULL,
    status TEXT NOT NULL,
    requested_storyboard_count INTEGER NOT NULL,
    input_material_count INTEGER NOT NULL,
    error_message TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TEXT,
    FOREIGN KEY (project_id) REFERENCES content_projects(id) ON DELETE CASCADE,
    FOREIGN KEY (selected_topic_candidate_id) REFERENCES topic_candidates(id) ON DELETE CASCADE,
    FOREIGN KEY (selected_script_draft_id) REFERENCES script_drafts(id) ON DELETE CASCADE,
    CHECK (status IN ('running', 'succeeded', 'failed'))
);

CREATE TABLE IF NOT EXISTS storyboard_drafts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    generation_run_id INTEGER NOT NULL,
    topic_candidate_id INTEGER NOT NULL,
    script_draft_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    visual_style TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft',
    selected_at TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES content_projects(id) ON DELETE CASCADE,
    FOREIGN KEY (generation_run_id) REFERENCES storyboard_generation_runs(id) ON DELETE CASCADE,
    FOREIGN KEY (topic_candidate_id) REFERENCES topic_candidates(id) ON DELETE CASCADE,
    FOREIGN KEY (script_draft_id) REFERENCES script_drafts(id) ON DELETE CASCADE,
    CHECK (status IN ('draft', 'selected', 'dismissed'))
);

CREATE TABLE IF NOT EXISTS storyboard_scenes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    storyboard_draft_id INTEGER NOT NULL,
    scene_order INTEGER NOT NULL,
    scene_title TEXT NOT NULL,
    narration TEXT NOT NULL,
    visual_description TEXT NOT NULL,
    on_screen_text TEXT NOT NULL,
    estimated_duration_seconds INTEGER NOT NULL,
    source_material_id INTEGER,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (storyboard_draft_id) REFERENCES storyboard_drafts(id) ON DELETE CASCADE,
    FOREIGN KEY (source_material_id) REFERENCES user_materials(id) ON DELETE SET NULL,
    CHECK (scene_order >= 1),
    CHECK (estimated_duration_seconds > 0)
);

CREATE TABLE IF NOT EXISTS storyboard_draft_sources (
    storyboard_draft_id INTEGER NOT NULL,
    material_id INTEGER NOT NULL,
    PRIMARY KEY (storyboard_draft_id, material_id),
    FOREIGN KEY (storyboard_draft_id) REFERENCES storyboard_drafts(id) ON DELETE CASCADE,
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

CREATE INDEX IF NOT EXISTS idx_script_generation_runs_project_id_created_at
ON script_generation_runs (project_id, created_at DESC, id DESC);

CREATE INDEX IF NOT EXISTS idx_script_drafts_project_id_created_at
ON script_drafts (project_id, created_at DESC, id DESC);

CREATE INDEX IF NOT EXISTS idx_storyboard_generation_runs_project_id_created_at
ON storyboard_generation_runs (project_id, created_at DESC, id DESC);

CREATE INDEX IF NOT EXISTS idx_storyboard_drafts_project_id_created_at
ON storyboard_drafts (project_id, created_at DESC, id DESC);

CREATE INDEX IF NOT EXISTS idx_storyboard_scenes_draft_order
ON storyboard_scenes (storyboard_draft_id, scene_order ASC, id ASC);
"""
