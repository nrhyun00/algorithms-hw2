"""URL 단축기. 코드는 일련번호를 base62로 바꾼 것이다."""

from base62 import encode
from hash_table import HashTable

MAX_URL_LENGTH = 2048


def validate(url):
    if not isinstance(url, str):
        raise ValueError("URL은 문자열이어야 합니다")
    url = url.strip()
    if url == "":
        raise ValueError("빈 URL입니다")
    if len(url) > MAX_URL_LENGTH:
        raise ValueError(f"URL이 {MAX_URL_LENGTH}자를 넘습니다")
    for ch in url:
        if ch.isspace():
            raise ValueError("URL에 공백이 있습니다")
    if url.startswith("http://"):
        rest = url[len("http://"):]
    elif url.startswith("https://"):
        rest = url[len("https://"):]
    else:
        raise ValueError("http:// 또는 https:// 주소만 받습니다")
    host = rest
    for sep in "/?#":
        host = host.split(sep, 1)[0]
    if host == "":
        raise ValueError("호스트가 없습니다")
    return url


class Shortener:
    def __init__(self, table_cls=HashTable):
        self.table_cls = table_cls
        self._url_to_code = table_cls()
        self._code_to_url = table_cls()
        self._next = 1

    def __len__(self):
        return len(self._code_to_url)

    def code_table(self):
        return self._code_to_url

    def url_table(self):
        return self._url_to_code

    def shorten(self, url):
        url = validate(url)
        code = self._url_to_code.get(url)
        if code is not None:
            return code
        code = encode(self._next)
        self._next += 1
        self._url_to_code.put(url, code)
        self._code_to_url.put(code, url)
        return code

    def expand(self, code):
        if not isinstance(code, str):
            return None
        return self._code_to_url.get(code)
