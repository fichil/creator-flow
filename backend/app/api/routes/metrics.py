from fastapi import APIRouter, Depends, HTTPException, status

from app.db.database import get_db
from app.metrics.fake_metrics import FakeMetricsProvider
from app.metrics.provider import MetricsSnapshotInput
from app.schemas.metrics import PublicationMetricSnapshotResponse

router = APIRouter()


@router.get(
    "/{project_id}/publication-records/{publication_record_id}/metrics",
    response_model=list[PublicationMetricSnapshotResponse],
)
def list_publication_metric_snapshots(project_id: int, publication_record_id: int, db=Depends(get_db)):
    _get_project(db, project_id)
    _get_publication_record(db, project_id, publication_record_id)
    rows = db.execute(
        """
        SELECT id, project_id, publication_record_id, source, captured_at,
               views, likes, comments, shares, favorites, average_watch_time_seconds,
               completion_rate, provider_payload_summary, created_at, updated_at
        FROM publication_metric_snapshots
        WHERE project_id = ? AND publication_record_id = ?
        ORDER BY captured_at DESC, id DESC
        """,
        (project_id, publication_record_id),
    ).fetchall()
    return [dict(row) for row in rows]


@router.post(
    "/{project_id}/publication-records/{publication_record_id}/metrics/fake",
    response_model=PublicationMetricSnapshotResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_fake_publication_metric_snapshot(project_id: int, publication_record_id: int, db=Depends(get_db)):
    project = _get_project(db, project_id)
    _ensure_project_mutable(project, "create fake metrics snapshots")
    publication_record = _get_publication_record(db, project_id, publication_record_id)

    provider = FakeMetricsProvider()
    result = provider.collect(
        MetricsSnapshotInput(
            project_id=project_id,
            publish_intent_id=publication_record["publish_intent_id"],
            publication_record_id=publication_record["id"],
            target_platform=publication_record["target_platform"],
            provider_name=publication_record["provider_name"],
            publication_status=publication_record["publication_status"],
        )
    )
    row = db.execute(
        """
        INSERT INTO publication_metric_snapshots (
            project_id, publication_record_id, source, views, likes, comments, shares,
            favorites, average_watch_time_seconds, completion_rate, provider_payload_summary
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        RETURNING id, project_id, publication_record_id, source, captured_at,
                  views, likes, comments, shares, favorites, average_watch_time_seconds,
                  completion_rate, provider_payload_summary, created_at, updated_at
        """,
        (
            project_id,
            publication_record_id,
            result.source,
            result.views,
            result.likes,
            result.comments,
            result.shares,
            result.favorites,
            result.average_watch_time_seconds,
            result.completion_rate,
            result.provider_payload_summary,
        ),
    ).fetchone()
    db.commit()
    return dict(row)


@router.get(
    "/{project_id}/publication-records/{publication_record_id}/metrics/{metric_snapshot_id}",
    response_model=PublicationMetricSnapshotResponse,
)
def get_publication_metric_snapshot(
    project_id: int,
    publication_record_id: int,
    metric_snapshot_id: int,
    db=Depends(get_db),
):
    _get_project(db, project_id)
    _get_publication_record(db, project_id, publication_record_id)
    return _get_metric_snapshot(db, project_id, publication_record_id, metric_snapshot_id)


def _get_project(db, project_id: int):
    project = db.execute(
        """
        SELECT id, title, description, status
        FROM content_projects
        WHERE id = ?
        """,
        (project_id,),
    ).fetchone()
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="project not found")
    return project


def _ensure_project_mutable(project, action: str) -> None:
    if project["status"] == "archived":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"archived project cannot {action}",
        )


def _get_publication_record(db, project_id: int, publication_record_id: int) -> dict:
    row = db.execute(
        """
        SELECT id, project_id, publish_intent_id, target_platform, provider_name,
               external_publication_id, publication_status, error_message, created_at, updated_at
        FROM publication_records
        WHERE id = ? AND project_id = ?
        """,
        (publication_record_id, project_id),
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="publication record not found")
    return dict(row)


def _get_metric_snapshot(db, project_id: int, publication_record_id: int, metric_snapshot_id: int) -> dict:
    row = db.execute(
        """
        SELECT id, project_id, publication_record_id, source, captured_at,
               views, likes, comments, shares, favorites, average_watch_time_seconds,
               completion_rate, provider_payload_summary, created_at, updated_at
        FROM publication_metric_snapshots
        WHERE id = ? AND project_id = ? AND publication_record_id = ?
        """,
        (metric_snapshot_id, project_id, publication_record_id),
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="metric snapshot not found")
    return dict(row)
