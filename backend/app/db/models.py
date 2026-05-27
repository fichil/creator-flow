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

CREATE TABLE IF NOT EXISTS content_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    account_positioning TEXT NOT NULL,
    content_type TEXT NOT NULL,
    target_frequency_per_week INTEGER NOT NULL,
    preferences TEXT,
    is_enabled INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES content_projects(id) ON DELETE CASCADE,
    CHECK (target_frequency_per_week BETWEEN 1 AND 14),
    CHECK (is_enabled IN (0, 1))
);

CREATE TABLE IF NOT EXISTS generation_schedules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    content_plan_id INTEGER NOT NULL,
    frequency_per_week INTEGER NOT NULL,
    timezone TEXT NOT NULL,
    preferred_days TEXT,
    preferred_time TEXT NOT NULL,
    is_enabled INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES content_projects(id) ON DELETE CASCADE,
    FOREIGN KEY (content_plan_id) REFERENCES content_plans(id) ON DELETE CASCADE,
    CHECK (frequency_per_week BETWEEN 1 AND 14),
    CHECK (length(preferred_time) = 5),
    CHECK (is_enabled IN (0, 1))
);

CREATE TABLE IF NOT EXISTS generation_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    content_plan_id INTEGER NOT NULL,
    generation_schedule_id INTEGER,
    status TEXT NOT NULL DEFAULT 'queued',
    trigger_type TEXT NOT NULL,
    input_summary TEXT NOT NULL,
    result_summary TEXT,
    error_message TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES content_projects(id) ON DELETE CASCADE,
    FOREIGN KEY (content_plan_id) REFERENCES content_plans(id) ON DELETE CASCADE,
    FOREIGN KEY (generation_schedule_id) REFERENCES generation_schedules(id) ON DELETE SET NULL,
    CHECK (status IN ('queued', 'running', 'succeeded', 'failed')),
    CHECK (trigger_type IN ('manual', 'scheduled'))
);

CREATE TABLE IF NOT EXISTS review_drafts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    content_plan_id INTEGER NOT NULL,
    generation_schedule_id INTEGER,
    generation_run_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    draft_summary TEXT NOT NULL,
    input_source_summary TEXT NOT NULL,
    hotspot_source_summary TEXT,
    review_status TEXT NOT NULL DEFAULT 'pending_review',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES content_projects(id) ON DELETE CASCADE,
    FOREIGN KEY (content_plan_id) REFERENCES content_plans(id) ON DELETE CASCADE,
    FOREIGN KEY (generation_schedule_id) REFERENCES generation_schedules(id) ON DELETE SET NULL,
    FOREIGN KEY (generation_run_id) REFERENCES generation_runs(id) ON DELETE CASCADE,
    CHECK (review_status IN ('pending_review', 'approved', 'rejected'))
);

CREATE TABLE IF NOT EXISTS publish_intents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    review_draft_id INTEGER NOT NULL,
    target_platform TEXT NOT NULL,
    title TEXT NOT NULL,
    caption TEXT NOT NULL,
    publish_status TEXT NOT NULL DEFAULT 'pending_confirmation',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES content_projects(id) ON DELETE CASCADE,
    FOREIGN KEY (review_draft_id) REFERENCES review_drafts(id) ON DELETE CASCADE,
    CHECK (publish_status IN ('pending_confirmation', 'confirmed', 'cancelled'))
);

CREATE TABLE IF NOT EXISTS publication_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    publish_intent_id INTEGER NOT NULL,
    target_platform TEXT NOT NULL,
    provider_name TEXT NOT NULL,
    external_publication_id TEXT,
    publication_status TEXT NOT NULL DEFAULT 'not_started',
    error_message TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES content_projects(id) ON DELETE CASCADE,
    FOREIGN KEY (publish_intent_id) REFERENCES publish_intents(id) ON DELETE CASCADE,
    CHECK (publication_status IN ('not_started', 'succeeded', 'failed'))
);

CREATE TABLE IF NOT EXISTS publication_metric_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    publication_record_id INTEGER NOT NULL,
    source TEXT NOT NULL,
    captured_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    views INTEGER,
    likes INTEGER,
    comments INTEGER,
    shares INTEGER,
    favorites INTEGER,
    average_watch_time_seconds REAL,
    completion_rate REAL,
    provider_payload_summary TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES content_projects(id) ON DELETE CASCADE,
    FOREIGN KEY (publication_record_id) REFERENCES publication_records(id) ON DELETE CASCADE,
    CHECK (source IN ('fake_local', 'platform_provider')),
    CHECK (views IS NULL OR views >= 0),
    CHECK (likes IS NULL OR likes >= 0),
    CHECK (comments IS NULL OR comments >= 0),
    CHECK (shares IS NULL OR shares >= 0),
    CHECK (favorites IS NULL OR favorites >= 0),
    CHECK (average_watch_time_seconds IS NULL OR average_watch_time_seconds >= 0),
    CHECK (completion_rate IS NULL OR (completion_rate >= 0 AND completion_rate <= 1))
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

CREATE TABLE IF NOT EXISTS render_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    storyboard_draft_id INTEGER NOT NULL,
    renderer_name TEXT NOT NULL,
    renderer_version TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'queued',
    requested_format TEXT NOT NULL DEFAULT 'mp4',
    requested_aspect_ratio TEXT NOT NULL DEFAULT '9:16',
    requested_resolution TEXT NOT NULL DEFAULT '1080x1920',
    error_message TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    started_at TEXT,
    completed_at TEXT,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES content_projects(id) ON DELETE CASCADE,
    FOREIGN KEY (storyboard_draft_id) REFERENCES storyboard_drafts(id) ON DELETE CASCADE,
    CHECK (status IN ('queued', 'running', 'succeeded', 'failed')),
    CHECK (requested_format IN ('mp4')),
    CHECK (requested_aspect_ratio IN ('9:16')),
    CHECK (requested_resolution IN ('1080x1920'))
);

CREATE TABLE IF NOT EXISTS render_artifacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    render_job_id INTEGER NOT NULL,
    subtitle_draft_id INTEGER,
    artifact_type TEXT NOT NULL DEFAULT 'fake_preview_manifest',
    file_name TEXT NOT NULL,
    mime_type TEXT NOT NULL,
    file_size_bytes INTEGER NOT NULL,
    duration_seconds INTEGER NOT NULL,
    width INTEGER NOT NULL,
    height INTEGER NOT NULL,
    storage_path TEXT NOT NULL,
    checksum_sha256 TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES content_projects(id) ON DELETE CASCADE,
    FOREIGN KEY (render_job_id) REFERENCES render_jobs(id) ON DELETE CASCADE,
    FOREIGN KEY (subtitle_draft_id) REFERENCES subtitle_drafts(id) ON DELETE SET NULL,
    CHECK (artifact_type IN ('fake_video', 'fake_preview_manifest')),
    CHECK (mime_type IN ('video/mp4', 'application/json')),
    CHECK (file_size_bytes >= 0),
    CHECK (duration_seconds > 0),
    CHECK (width > 0),
    CHECK (height > 0)
);

CREATE TABLE IF NOT EXISTS subtitle_drafts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    script_draft_id INTEGER NOT NULL,
    storyboard_draft_id INTEGER NOT NULL,
    generator_name TEXT NOT NULL,
    generator_version TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft',
    selected_at TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES content_projects(id) ON DELETE CASCADE,
    FOREIGN KEY (script_draft_id) REFERENCES script_drafts(id) ON DELETE CASCADE,
    FOREIGN KEY (storyboard_draft_id) REFERENCES storyboard_drafts(id) ON DELETE CASCADE,
    CHECK (status IN ('draft', 'selected', 'dismissed'))
);

CREATE TABLE IF NOT EXISTS subtitle_cues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subtitle_draft_id INTEGER NOT NULL,
    cue_order INTEGER NOT NULL,
    start_time_seconds INTEGER NOT NULL,
    end_time_seconds INTEGER NOT NULL,
    text TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subtitle_draft_id) REFERENCES subtitle_drafts(id) ON DELETE CASCADE,
    CHECK (cue_order >= 1),
    CHECK (start_time_seconds >= 0),
    CHECK (end_time_seconds > start_time_seconds)
);

CREATE INDEX IF NOT EXISTS idx_content_projects_created_at
ON content_projects (created_at DESC, id DESC);

CREATE INDEX IF NOT EXISTS idx_user_materials_project_id_created_at
ON user_materials (project_id, created_at DESC, id DESC);

CREATE INDEX IF NOT EXISTS idx_content_plans_project_id_created_at
ON content_plans (project_id, created_at DESC, id DESC);

CREATE INDEX IF NOT EXISTS idx_generation_schedules_project_id_created_at
ON generation_schedules (project_id, created_at DESC, id DESC);

CREATE INDEX IF NOT EXISTS idx_generation_schedules_content_plan_id
ON generation_schedules (content_plan_id);

CREATE INDEX IF NOT EXISTS idx_generation_runs_project_id_created_at
ON generation_runs (project_id, created_at DESC, id DESC);

CREATE INDEX IF NOT EXISTS idx_generation_runs_content_plan_id
ON generation_runs (content_plan_id);

CREATE INDEX IF NOT EXISTS idx_review_drafts_project_id_created_at
ON review_drafts (project_id, created_at DESC, id DESC);

CREATE INDEX IF NOT EXISTS idx_review_drafts_generation_run_id
ON review_drafts (generation_run_id);

CREATE INDEX IF NOT EXISTS idx_publish_intents_project_id_created_at
ON publish_intents (project_id, created_at DESC, id DESC);

CREATE INDEX IF NOT EXISTS idx_publish_intents_review_draft_id
ON publish_intents (review_draft_id);

CREATE INDEX IF NOT EXISTS idx_publication_records_project_id_created_at
ON publication_records (project_id, created_at DESC, id DESC);

CREATE INDEX IF NOT EXISTS idx_publication_records_publish_intent_id
ON publication_records (publish_intent_id);

CREATE INDEX IF NOT EXISTS idx_publication_metric_snapshots_record_captured_at
ON publication_metric_snapshots (publication_record_id, captured_at DESC, id DESC);

CREATE INDEX IF NOT EXISTS idx_publication_metric_snapshots_project_id_created_at
ON publication_metric_snapshots (project_id, created_at DESC, id DESC);

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

CREATE INDEX IF NOT EXISTS idx_render_jobs_project_id_created_at
ON render_jobs (project_id, created_at DESC, id DESC);

CREATE INDEX IF NOT EXISTS idx_render_artifacts_render_job_id
ON render_artifacts (render_job_id);

CREATE INDEX IF NOT EXISTS idx_subtitle_drafts_project_id_created_at
ON subtitle_drafts (project_id, created_at DESC, id DESC);

CREATE INDEX IF NOT EXISTS idx_subtitle_cues_draft_order
ON subtitle_cues (subtitle_draft_id, cue_order ASC, id ASC);
"""
