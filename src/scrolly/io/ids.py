import uuid


def stable_id(source: str, key: str) -> str:
    """The same imported row always gets the same id, so importing twice adds nothing."""
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"scrolly:{source}:{key}"))
