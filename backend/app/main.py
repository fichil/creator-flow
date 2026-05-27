from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    content_plans,
    generation_runs,
    generation_schedules,
    health,
    materials,
    metric_review_summaries,
    metrics,
    provider_connections,
    provider_registry,
    projects,
    publishing,
    render_jobs,
    review_drafts,
    script_drafts,
    storyboards,
    subtitle_drafts,
    topic_candidates,
)
from app.core.config import get_settings
from app.db.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db(get_settings())
    yield


app = FastAPI(title="creator-flow", version="0.1.0", lifespan=lifespan)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(provider_registry.router, prefix="/api/providers", tags=["providers"])
app.include_router(
    provider_connections.router,
    prefix="/api/provider-connections",
    tags=["provider-connections"],
)
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(materials.router, prefix="/api/projects", tags=["materials"])
app.include_router(content_plans.router, prefix="/api/projects", tags=["content-plans"])
app.include_router(generation_schedules.router, prefix="/api/projects", tags=["generation-schedules"])
app.include_router(generation_runs.router, prefix="/api/projects", tags=["generation-runs"])
app.include_router(review_drafts.router, prefix="/api/projects", tags=["review-drafts"])
app.include_router(publishing.router, prefix="/api/projects", tags=["publishing"])
app.include_router(metrics.router, prefix="/api/projects", tags=["metrics"])
app.include_router(
    metric_review_summaries.router,
    prefix="/api/projects",
    tags=["metric-review-summaries"],
)
app.include_router(topic_candidates.router, prefix="/api/projects", tags=["topic-candidates"])
app.include_router(script_drafts.router, prefix="/api/projects", tags=["script-drafts"])
app.include_router(storyboards.router, prefix="/api/projects", tags=["storyboards"])
app.include_router(subtitle_drafts.router, prefix="/api/projects", tags=["subtitle-drafts"])
app.include_router(render_jobs.router, prefix="/api/projects", tags=["renders"])
