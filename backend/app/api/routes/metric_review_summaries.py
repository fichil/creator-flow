from fastapi import APIRouter, Depends, HTTPException, status

from app.db.database import get_db
from app.metrics.fake_review_summary import FakeMetricsReviewSummaryGenerator, MetricsReviewSnapshot
from app.schemas.metric_review_summary import PublicationMetricReviewSummaryResponse

router = APIRouter()


@router.get(
    "/{project_id}/publication-records/{publication_record_id}/metric-review-summaries",
    response_model=list[PublicationMetricReviewSummaryResponse],
)
def list_publication_metric_review_summaries(project_id: int, publication_record_id: int, db=Depends(get_db)):
    _get_project(db, project_id)
    _get_publication_record(db, project_id, publication_record_id)
    rows = db.execute(
        """
        SELECT id, project_id, publication_record_id, source, is_fake_local, summary_text,
               highlights, low_performance_signals, next_observations, snapshot_count,
               metric_window_start, metric_window_end, created_at, updated_at
        FROM publication_metric_review_summaries
        WHERE project_id = ? AND publication_record_id = ?
        ORDER BY created_at DESC, id DESC
        """,
        (project_id, publication_record_id),
    ).fetchall()
    return [dict(row) for row in rows]


@router.post(
    "/{project_id}/publication-records/{publication_record_id}/metric-review-summaries/fake",
    response_model=PublicationMetricReviewSummaryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_fake_publication_metric_review_summary(project_id: int, publication_record_id: int, db=Depends(get_db)):
    project = _get_project(db, project_id)
    _ensure_project_mutable(project, "create fake metric review summaries")
    _get_publication_record(db, project_id, publication_record_id)
    snapshots = _list_metric_snapshots(db, project_id, publication_record_id)
    result = FakeMetricsReviewSummaryGenerator().generate(snapshots)

    row = db.execute(
        """
        INSERT INTO publication_metric_review_summaries (
            project_id, publication_record_id, source, is_fake_local, summary_text,
            highlights, low_performance_signals, next_observations, snapshot_count,
            metric_window_start, metric_window_end
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        RETURNING id, project_id, publication_record_id, source, is_fake_local, summary_text,
                  highlights, low_performance_signals, next_observations, snapshot_count,
                  metric_window_start, metric_window_end, created_at, updated_at
        """,
        (
            project_id,
            publication_record_id,
            result.source,
            1 if result.is_fake_local else 0,
            result.summary_text,
            result.highlights,
            result.low_performance_signals,
            result.next_observations,
            result.snapshot_count,
            result.metric_window_start,
            result.metric_window_end,
        ),
    ).fetchone()
    db.commit()
    return dict(row)


@router.get(
    "/{project_id}/publication-records/{publication_record_id}/metric-review-summaries/{summary_id}",
    response_model=PublicationMetricReviewSummaryResponse,
)
def get_publication_metric_review_summary(
    project_id: int,
    publication_record_id: int,
    summary_id: int,
    db=Depends(get_db),
):
    _get_project(db, project_id)
    _get_publication_record(db, project_id, publication_record_id)
    return _get_metric_review_summary(db, project_id, publication_record_id, summary_id)


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


def _list_metric_snapshots(db, project_id: int, publication_record_id: int) -> list[MetricsReviewSnapshot]:
    rows = db.execute(
        """
        SELECT captured_at, views, likes, comments, shares, favorites,
               average_watch_time_seconds, completion_rate
        FROM publication_metric_snapshots
        WHERE project_id = ? AND publication_record_id = ?
        ORDER BY captured_at ASC, id ASC
        """,
        (project_id, publication_record_id),
    ).fetchall()
    return [
        MetricsReviewSnapshot(
            captured_at=row["captured_at"],
            views=row["views"],
            likes=row["likes"],
            comments=row["comments"],
            shares=row["shares"],
            favorites=row["favorites"],
            average_watch_time_seconds=row["average_watch_time_seconds"],
            completion_rate=row["completion_rate"],
        )
        for row in rows
    ]


def _get_metric_review_summary(db, project_id: int, publication_record_id: int, summary_id: int) -> dict:
    row = db.execute(
        """
        SELECT id, project_id, publication_record_id, source, is_fake_local, summary_text,
               highlights, low_performance_signals, next_observations, snapshot_count,
               metric_window_start, metric_window_end, created_at, updated_at
        FROM publication_metric_review_summaries
        WHERE id = ? AND project_id = ? AND publication_record_id = ?
        """,
        (summary_id, project_id, publication_record_id),
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="metric review summary not found")
    return dict(row)
