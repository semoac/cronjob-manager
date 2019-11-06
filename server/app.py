from flask import Flask, jsonify
from flask_cors import CORS
from .managers import KubernetesManager
from .settings import NAMESPACES

# configuration
DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})
km = KubernetesManager(namespaces=NAMESPACES)


@app.route("/ping", methods=["GET"])
def ping_pong():
    return jsonify("pong!")


@app.route("/api/v1/namespaces", methods=["GET"])
def get_namespaces():
    return jsonify({"namespaces": NAMESPACES})


@app.route("/api/v1/cronjobs/<string:namespace>", methods=["GET"])
def get_cronjobs(namespace):
    manager = km.get_manager(namespace=namespace)

    CRONJOBS = {
        "namespace": namespace,
        "cronjobs": manager.map_namespaced_resources(),
        "status": "success",
    }
    return jsonify(CRONJOBS)


@app.route("/api/v1/cronjobs/<string:namespace>/<string:cronjob>", methods=["PATCH"])
def patch_cronjob(namespace, cronjob):
    manager = km.get_manager(namespace=namespace)
    manager.switchCronjobStatus(cronjob)
    return jsonify({"status": "ok"})


@app.route("/api/v1/job/<string:namespace>/<string:job>", methods=["DELETE"])
def delete_job(namespace, job):
    manager = km.get_manager(namespace=namespace)
    manager.deleteJob(job)
    return jsonify({"status": "ok"})


@app.route("/api/v1/job/<string:namespace>/<string:cronjob>", methods=["PUT"])
def new_job(namespace, cronjob):
    manager = km.get_manager(namespace=namespace)
    manager.newJob(cronjob)
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run()
