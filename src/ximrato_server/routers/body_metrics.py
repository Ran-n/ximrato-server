#!/usr/bin/env python3
"""
Authors: Ran# <ran.hash@proton.me>
Created: 2026/03/27 00:00:00.000000
Revised: 2026/03/27 20:24:47.139374
"""

import logging

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ximrato_server.database import get_db
from ximrato_server.deps import get_current_user
from ximrato_server.models.body_metric import BodyMetric
from ximrato_server.models.lookup import MetricType
from ximrato_server.models.user import User
from ximrato_server.schemas.body_metric import BodyMetricResponse, CreateBodyMetricRequest

log = logging.getLogger("ximrato.body_metrics")

router = APIRouter(prefix="/body-metrics", tags=["body-metrics"])


@router.post("", response_model=BodyMetricResponse, status_code=status.HTTP_201_CREATED)
def create_body_metric(
    body: CreateBodyMetricRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    log.info("create_body_metric: user_id=%d type=%s", current_user.id, body.metric_type)
    mt = db.scalar(select(MetricType).where(MetricType.name == body.metric_type))
    metric = BodyMetric(
        user_id=current_user.id,
        metric_type_id=mt.id,
        value=body.value,
    )
    db.add(metric)
    db.commit()
    db.refresh(metric)
    log.info("create_body_metric: id=%d", metric.id)
    return db.scalar(
        select(BodyMetric).where(BodyMetric.id == metric.id).options(selectinload(BodyMetric.metric_type_rel))
    )


@router.get("", response_model=list[BodyMetricResponse])
def list_body_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    log.info("list_body_metrics: user_id=%d", current_user.id)
    return db.scalars(
        select(BodyMetric)
        .where(BodyMetric.user_id == current_user.id)
        .order_by(BodyMetric.logged_at.desc(), BodyMetric.id.desc())
        .options(selectinload(BodyMetric.metric_type_rel))
    ).all()
