from celery import Task

from h.celery import celery, get_task_logger

log = get_task_logger(__name__)


# See: https://docs.celeryproject.org/en/stable/userguide/tasks.html#automatic-retry-for-known-exceptions
class _BaseTaskWithRetry(Task):
    autoretry_for = (Exception,)
    retry_kwargs = {"max_retries": 5}
    # Add exponential back-off
    retry_backoff = True
    # Shuffle the times a bit to prevent the thundering herd problem
    retry_jitter = True


@celery.task(base=_BaseTaskWithRetry)
def add_annotation(id_):
    search_index = celery.request.find_service(name="search_index")
    search_index.add_annotation_by_id(id_)


@celery.task
def add_annotations_between_times(start_time, end_time, tag):
    celery.request.find_service(
        name="search_index"
    )._queue.add_annotations_between_times(start_time, end_time, tag)


@celery.task
def add_users_annotations(userid, tag, force, schedule_in):
    celery.request.find_service(name="search_index")._queue.add_users_annotations(
        userid, tag, force=force, schedule_in=schedule_in
    )


@celery.task(base=_BaseTaskWithRetry)
def delete_annotation(id_):
    search_index = celery.request.find_service(name="search_index")
    search_index.delete_annotation_by_id(id_)


@celery.task(acks_late=False)
def sync_annotations(limit):
    celery.request.find_service(name="search_index").sync(limit)
