import os

_TARGET_NAMESPACES = os.environ.get("NAMESPACES", "default,")

NAMESPACES = [x for x in filter(None, _TARGET_NAMESPACES.split(","))]
ENVIRONMENT = os.environ.get("ENVIRONMENT", "localhost")

__all__ = ["NAMESPACES", "ENVIRONMENT"]
