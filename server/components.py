import json
import queue
import signal
import threading
import time
import typing
import uuid
from datetime import datetime

from prometheus_client import Counter, Gauge

from server.backend_logger import get_logger

logger = get_logger()


class Document:

    def __init__(self, version: str, channel: str, payload: dict):
        self.data = dict()
        self.data["timestamp"] = str(datetime.now())
        self.data["id"] = str(uuid.uuid4())
        self.data["payload"] = payload
        self.data["channel"] = channel
        self.data["version"] = version

    def __str__(self) -> str:
        return f'Document: {self.data}'

    #customize the serialization if needed
    def serialize(self):
        return json.dumps(self.data)


bucket_gauge = Gauge('current_bucket_amount', 'Current Documents Amount')


class Bucket:
    counter_files_written = Counter('flush', 'Files written')

    def __init__(self, size: int):
        self.cache = dict()
        self.size = size
        self.creation_time = datetime.now()

    def _push(self, doc_id: str, doc: Document) -> str:
        if len(self.cache) == 0:
            self.creation_time = datetime.now()

        self.cache[doc_id] = doc
        bucket_gauge.inc(amount=1)

        if len(self.cache) >= self.size:
            logger.debug("Bucket overflow, flushing all documents")
            self.flush()
        return doc_id

    def create(self, doc: Document) -> typing.Optional[str]:
        return self._push(doc=doc, doc_id=str(uuid.uuid4()))

    def read(self, doc_id: str) -> typing.Optional[Document]:
        if doc_id in self.cache:
            return self.cache[doc_id]
        else:
            return None

    def update(self, doc_id: str, doc: Document) -> typing.Optional[str]:
        previous_doc = self.read(doc_id=doc_id)
        if previous_doc is None:
            return None
        else:
            return self._push(doc=doc, doc_id=doc_id)

    def delete(self, doc_id: str):
        if doc_id is not None:
            self.cache.pop(doc_id, None)

    def clear(self):
        logger.debug("Clear bucket cache")
        self.cache.clear()
        self.creation_time = datetime.now()

    # Override this and write wherever you want
    def flush(self):
        if len(self.cache) == 0:
            logger.debug("Bucket is empty, skip flushing...")
            self.clear()
            return
        self.counter_files_written.inc()
        logger.debug("***********************************")
        logger.debug("Flushing %d serialized documents", len(self.cache))
        amount = len(self.cache)
        for key in self.cache.keys():
            logger.debug(self.cache[key].serialize())
        logger.debug("***********************************")
        self.clear()
        bucket_gauge.dec(amount=amount)


class BucketManager:

    def __init__(self, size: int, bucket_timeout_in_seconds: int):
        self.is_alive = True
        self.bucket = Bucket(size=size)
        self.bucket_timeout_in_seconds = bucket_timeout_in_seconds
        self.q = queue.Queue()

    def kill(self):
        self.is_alive = False

    def start(self):
        threading.Thread(target=self._work, daemon=True, name="Bucket-Manager-Thread").start()

    def _work(self):
        while self.is_alive:
            if len(self.bucket.cache) > 0 and self._bucket_age_in_seconds() >= self.bucket_timeout_in_seconds:
                logger.debug("Bucket timeout, flushing all documents")
                self.bucket.flush()
                continue

            if not self.q.empty():
                doc = self.q.get_nowait()
                if doc is not None:
                    self.bucket.create(doc)

            time.sleep(1.0)
            logger.info("Heart beat from Bucket Manager, Bucket age %d [s]", self._bucket_age_in_seconds())

        if len(self.bucket.cache) > 0:
            logger.debug("Teardown in progress, flushing leftovers")
            self.bucket.flush()
        else:
            logger.debug("No leftovers, no flushing required")
        logger.info("Bucket manager closed, bye...")

    def push(self, doc: Document):
        self.q.put(doc)

    def _bucket_age_in_seconds(self) -> int:
        if len(self.bucket.cache) > 0:
            return (datetime.now() - self.bucket.creation_time).seconds
        else:
            return -1


class GracefulShutdown:

    def __init__(self, shutdown_function):
        self.kill_now = False
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)
        self.shutdown_function = shutdown_function
        threading.Thread(target=self._start_shutdown, daemon=True, name="Graceful-Shutdown-Thread").start()

    def exit_gracefully(self, *args):
        self.kill_now = True

    def _start_shutdown(self):
        while not self.kill_now:
            time.sleep(1.0)

        self.shutdown_function()

