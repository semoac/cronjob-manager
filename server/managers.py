from __future__ import annotations
from typing import List, Dict, TypeVar
from datetime import datetime
from kubernetes import client, config
from .schemas import PodSchema, JobSchema, CronjobSchema, Cronjob, Job, Pod
from .settings import ENVIRONMENT


class Manager(object):
    manager: CronjobManager
    updated_at: datetime

    def __init__(self, manager: CronjobManager, updated_at: datetime):
        self.manager = manager
        self.updated_at = updated_at


class KubernetesManager(object):
    TTL = 5
    CronJobManagers: Dict[str, Manager] = {}

    def __init__(self, namespaces: List[str]):
        for namespace in namespaces:
            manager = CronjobManager(namespace)
            self.CronJobManagers[namespace] = Manager(
                manager=manager, updated_at=datetime.now()
            )

    def get_manager(self, namespace: str) -> CronjobManager:
        manager = self.CronJobManagers[namespace]
        time_diff = datetime.now() - manager.updated_at
        if time_diff.total_seconds() > self.TTL:
            manager.manager.sync_resouces()
            manager.updated_at = datetime.now()

        return manager.manager


class CronjobManager(object):
    def __init__(self, namespace: str = "default"):
        if ENVIRONMENT == "production":
            config.load_incluster_config()
        else:
            config.load_kube_config()
        self.core_v1 = client.CoreV1Api()
        self.batch_v1 = client.BatchV1Api()
        self.batch_v1beta1 = client.BatchV1beta1Api()
        self.namespace = namespace
        self.cronjobs = None
        self.jobs = None
        self.pods = None
        self.sync_resouces()

    def sync_resouces(self):
        raw_cronjobs = self.batch_v1beta1.list_namespaced_cron_job(
            namespace=self.namespace
        )
        raw_jobs = self.batch_v1.list_namespaced_job(namespace=self.namespace)
        raw_pods = self.core_v1.list_namespaced_pod(namespace=self.namespace)
        setattr(self, "cronjobs", raw_cronjobs)
        setattr(self, "jobs", raw_jobs)
        setattr(self, "pods", raw_pods)

    def map_namespaced_resources(self) -> List[Dict]:
        cronjob_list = []
        for cronjob_entry in self.cronjobs.items:
            cronjob_data = dict(
                name=cronjob_entry.metadata.name,
                schedule=cronjob_entry.spec.schedule,
                suspended=cronjob_entry.spec.suspend,
            )
            cronjob_obj = CronjobSchema().load(cronjob_data)
            jobs_obj = self._map_namespaced_jobs_from_cronjob(cronjob_obj)
            cronjob_obj.jobs = jobs_obj
            cronjob_list.append(cronjob_obj)

        return CronjobSchema().dump(cronjob_list, many=True)

    def _map_namespaced_jobs_from_cronjob(self, cronjob: Cronjob) -> List[Job]:
        job_list = []
        for job in self.jobs.items:
            if (
                job.metadata.owner_references
                and job.metadata.owner_references[0].kind == "CronJob"
                and job.metadata.owner_references[0].name == cronjob.name
            ):
                job_data = dict(
                    name=job.metadata.name,
                    start_at=(lambda date: str(date) if date is not None else None)(
                        job.status.start_time
                    ),
                    finish_at=(lambda date: str(date) if date is not None else None)(
                        job.status.completion_time
                    ),
                    backoff_limit=job.spec.backoff_limit,
                    deadline_seconds=job.spec.active_deadline_seconds or 0,
                    success_count=(lambda count: count or 0)(job.status.succeeded),
                    failure_count=(lambda count: count or 0)(job.status.failed),
                    active=job.status.active or False,
                )
                job_obj = JobSchema().load(job_data)
                job_obj.parent = cronjob
                pods = self._map_namespaced_pod_from_job(job_obj)
                job_obj.pods = pods
                job_list.append(job_obj)

        return job_list

    def _map_namespaced_pod_from_job(self, job: Job) -> List[Pod]:
        pod_list = []
        for pod in self.pods.items:
            if (
                pod.metadata.owner_references
                and pod.metadata.owner_references[0].kind == "Job"
                and pod.metadata.owner_references[0].name == job.name
            ):
                pod_data = dict(name=pod.metadata.name, phase=pod.status.phase)
                pod_obj = PodSchema().load(pod_data)
                pod_obj.parent = job
                pod_list.append(pod_obj)
        return pod_list

    def switchCronjobStatus(self, cronjob: str) -> None:
        cronjob_data = self.batch_v1beta1.read_namespaced_cron_job(
            cronjob, self.namespace
        )
        cronjob_data.spec.suspend = not cronjob_data.spec.suspend
        _ = self.batch_v1beta1.patch_namespaced_cron_job(
            cronjob, self.namespace, cronjob_data
        )
        return

    def deleteJob(self, job: str) -> None:
        _ = self.batch_v1.delete_namespaced_job(job, self.namespace)
        return

    def newJob(self, cronjob: str) -> None:
        _suffix = "-manual-{}".format(int(datetime.now().timestamp()))
        _template = self.batch_v1beta1.read_namespaced_cron_job(cronjob, self.namespace)
        if _template:
            _annotations = {"cronjob.kubernetes.io/instantiate": "manual"}
            _name = cronjob + _suffix
            _labels = _template.spec.job_template.metadata.labels
            _spec = _template.spec.job_template.spec
            _owner = client.V1OwnerReference(
                api_version="batch/v1beta1",
                block_owner_deletion=True,
                controller=True,
                kind="CronJob",
                name=cronjob,
                uid=_template.metadata.uid,
            )
            _metadata = client.V1ObjectMeta(
                annotations=_annotations,
                labels=_labels,
                name=_name,
                owner_references=[_owner],
            )

            _new_job = client.V1Job(
                api_version="batch/v1", kind="Job", spec=_spec, metadata=_metadata
            )

        _ = self.batch_v1.create_namespaced_job(namespace=self.namespace, body=_new_job)
        return
