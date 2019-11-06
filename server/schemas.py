from __future__ import annotations
from datetime import datetime
from typing import List
from marshmallow import Schema, fields, post_load


class Pod(object):
    def __init__(self, name: str, phase: str, parent: Job = None) -> None:
        self.name = name
        self.phase = phase
        self.parent = parent


class PodSchema(Schema):
    name = fields.Str()
    phase = fields.Str()
    parent = fields.Nested("JobSchema", only=("name",))

    @post_load
    def make_pod(self, data, **kwargs):
        return Pod(**data)


class Job(object):
    def __init__(
        self,
        name: str,
        start_at: datetime,
        finish_at: datetime,
        backoff_limit: int,
        deadline_seconds: int,
        success_count: int,
        failure_count: int,
        active: bool,
        pods: List[Pod] = [],
        parent: Cronjob = None,
    ):
        self.name = name
        self.start_at = start_at
        self.finish_at = finish_at
        self.backoff_limit = backoff_limit
        self.deadline_seconds = deadline_seconds
        self.success_count = success_count
        self.failure_count = failure_count
        self.active = active
        self.pods = pods
        self.parent = parent


class JobSchema(Schema):
    name = fields.Str()
    start_at = fields.DateTime(allow_none=True, missing=None)
    finish_at = fields.DateTime(allow_none=True, missing=None)
    backoff_limit = fields.Int()
    deadline_seconds = fields.Int()
    success_count = fields.Int()
    failure_count = fields.Int(default=0)
    active = fields.Bool()
    pods = fields.Nested(PodSchema, many=True)
    parent = fields.Nested("CronjobSchema", only=("name",))

    @post_load
    def make_job(self, data, **kwargs):
        return Job(**data)


class Cronjob(object):
    def __init__(self, name: str, schedule: str, suspended: bool, jobs: List[Job] = []):
        self.name = name
        self.schedule = schedule
        self.suspended = suspended
        self.jobs = jobs


class CronjobSchema(Schema):
    name = fields.Str()
    schedule = fields.Str()
    suspended = fields.Bool()
    jobs = fields.Nested(JobSchema, many=True)

    @post_load
    def make_cronjob(self, data, **kwargs):
        return Cronjob(**data)
