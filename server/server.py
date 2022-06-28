import json
import sys
import time

from flask import jsonify, request, Flask
from prometheus_client import Counter, start_http_server

from server.backend_logger import get_logger
from server.components import Bucket, Document, BucketManager, GracefulShutdown
from server.config_parser import ConfigurationParser

app = Flask(__name__)
logger = get_logger()

channel = "push_api_python"
version = "1.0.0"


class WorkerServer:

    bucket: Bucket
    shutdown_completed = False
    counter_404 = Counter('page_not_found', 'Not Found Requests')
    counter_create_request = Counter('create_document', 'Create Document Requests')

    def __init__(self, config: ConfigurationParser):
        self.graceful_shutdown = GracefulShutdown(self.graceful_shutdown)
        self.port = config.server_port()
        self.shutdown_timeout = config.shutdown_timeout()
        self.bucket_manager = BucketManager(size=config.bucket_size(), bucket_timeout_in_seconds=config.bucket_timeout())
        self.bucket_manager.start()
        self.init()

    def graceful_shutdown(self):
        logger.debug("Graceful shutdown function called with %d[s] of timeout", self.shutdown_timeout)
        self.bucket_manager.is_alive = False
        time.sleep(self.shutdown_timeout)
        logger.info("Worker shutdown completed, bye...")
        self.shutdown_completed = True
        sys.exit(0)

    def init(self):

        @app.route("/")
        def hello_world():
            return jsonify("Up and running"), 200

        @app.route('/api/v1/document', methods=['PUT'])
        def create_document():

            if self.graceful_shutdown.kill_now:
                logger.debug("Not acceptable request during shutdown phase")
                return jsonify("Shutdown in progress, please retry"), 410

            self.counter_create_request.inc()

            record = json.loads(request.data)
            doc = Document(channel=channel, version=version, payload=record)
            self.bucket_manager.push(doc)
            return jsonify("ok"), 201

        @app.errorhandler(404)
        def page_not_found(e):
            self.counter_404.inc()
            logger.warning("No route found %s", e)
            return jsonify("Not Found"), 404

    def start(self):
        logger.debug("Starting server at port %s", self.port)
        app.run(host="0.0.0.0", port=self.port)
