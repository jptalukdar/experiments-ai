import hashlib


def get_url_hash(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()
