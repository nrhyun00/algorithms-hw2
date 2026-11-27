"""URL 단축 웹 서버. 표준 모듈 http.server만 쓴다.

    python3 src/server.py --port 8000
"""

import argparse
import os
import sys
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hash_table import HashTable, R, horner_steps  # noqa: E402
from probing_table import LinearProbingTable  # noqa: E402
from shortener import Shortener  # noqa: E402

TABLES = [("chaining", HashTable), ("probing", LinearProbingTable)]

STYLE = """
body { font-family: sans-serif; max-width: 960px; margin: 2rem auto; padding: 0 1rem; color: #111; }
input[type=text] { width: 70%; padding: .5rem; font-size: 1rem; }
button { padding: .5rem 1rem; font-size: 1rem; }
.err { color: #b91c1c; }
.slot { display: flex; align-items: flex-start; gap: .4rem; margin: .3rem 0; flex-wrap: wrap; }
.idx { width: 3rem; font-weight: bold; text-align: right; padding-top: .4rem; }
.node { border: 1px solid #2563eb; border-radius: 6px; padding: .3rem .5rem; background: #eff6ff;
        font-size: .85rem; max-width: 22rem; overflow-wrap: anywhere; }
.empty { color: #9ca3af; padding-top: .4rem; }
.arrow { padding-top: .4rem; }
details { font-size: .8rem; color: #374151; }
nav a { margin-right: 1rem; }
"""


def page(title, body):
    return (f"<!doctype html><html lang='ko'><head><meta charset='utf-8'>"
            f"<meta name='viewport' content='width=device-width,initial-scale=1'>"
            f"<title>{escape(title)}</title><style>{STYLE}</style></head><body>"
            f"<nav><a href='/'>줄이기</a><a href='/table'>해시 테이블</a></nav>"
            f"<h1>{escape(title)}</h1>{body}</body></html>")


def form_html(message=""):
    return (f"{message}<form method='post' action='/shorten'>"
            f"<input type='text' name='url' placeholder='https://...' autofocus> "
            f"<button>줄이기</button></form>")


def horner_html(key, m):
    rows = "".join(
        f"<tr><td>{escape(ch)}</td><td>{o}</td><td>({R}·{h} + {o}) mod {m} = {nh}</td></tr>"
        for ch, o, h, nh in horner_steps(key, m)
    )
    return (f"<details><summary>호너 해시 계산</summary><table>"
            f"<tr><th>글자</th><th>ord</th><th>h</th></tr>{rows}</table></details>")


def node_html(key, code, base, m, extra=""):
    link = f"{base}/{code}"
    return (f"<div class='node'>{extra}<div><b>URL</b> {escape(key)}</div>"
            f"<div><b>코드</b> {escape(code)}</div>"
            f"<div><b>짧은 링크</b> <a href='{escape(link)}'>{escape(link)}</a></div>"
            f"{horner_html(key, m)}</div>")


def chaining_html(t, base):
    m = t.capacity()
    parts = []
    for i, chain in enumerate(t.chains()):
        if not chain:
            cells = "<span class='empty'>∅</span>"
        else:
            cells = "<span class='arrow'>→</span>".join(
                node_html(k, v, base, m) for k, v in chain) + "<span class='arrow'>→ ∅</span>"
        parts.append(f"<div class='slot'><span class='idx'>[{i}]</span>{cells}</div>")
    return "".join(parts)


def probing_html(t, base):
    m = t.capacity()
    parts = []
    for i, slot in enumerate(t.slots()):
        if slot is None:
            cell = "<span class='empty'>빈 칸</span>"
        else:
            key, code, home, looked = slot
            moved = "처음 칸 그대로" if looked == 1 else f"{looked - 1}칸 밀려남"
            extra = (f"<div><b>처음 칸</b> [{home}] → 여기까지 <b>{looked}칸을 봄</b>"
                     f" ({moved})</div>")
            cell = node_html(key, code, base, m, extra)
        parts.append(f"<div class='slot'><span class='idx'>[{i}]</span>{cell}</div>")
    return "".join(parts)


def table_html(t, base):
    if isinstance(t, LinearProbingTable):
        return probing_html(t, base)
    return chaining_html(t, base)


class ShortenerHandler(BaseHTTPRequestHandler):
    shortener = None
    table_name = "chaining"

    def base_url(self):
        fwd = self.headers.get("X-Forwarded-Host")
        if fwd:
            proto = self.headers.get("X-Forwarded-Proto", "https")
            return f"{proto}://{fwd.split(',')[0].strip()}"
        host = self.headers.get("Host") or f"localhost:{self.server.server_address[1]}"
        return f"http://{host}"

    def send_page(self, status, html):
        body = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/":
            self.send_page(200, page("URL 단축기", form_html()))
        elif path == "/table":
            t = self.shortener.url_table()
            info = (f"<p>방식: <b>{self.table_name}</b> · 칸 수 M = {t.capacity()} · "
                    f"개수 n = {len(t)} · 적재율 α = {t.load_factor():.3f} · "
                    f"h = (31·h + ord(c)) mod M</p>")
            self.send_page(200, page("해시 테이블", info + table_html(t, self.base_url())))
        elif path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
        else:
            url = self.shortener.expand(path[1:])
            if url is None:
                self.send_page(404, page("없는 링크", "<p class='err'>그런 짧은 링크가 없습니다.</p>"))
            else:
                self.send_response(302)
                self.send_header("Location", url)
                self.send_header("Content-Length", "0")
                self.end_headers()

    def do_POST(self):
        if self.path != "/shorten":
            self.send_page(404, page("없는 주소", ""))
            return
        length = int(self.headers.get("Content-Length") or 0)
        data = parse_qs(self.rfile.read(length).decode("utf-8"))
        url = (data.get("url") or [""])[0]
        try:
            code = self.shortener.shorten(url)
        except ValueError as e:
            msg = f"<p class='err'>{escape(str(e))}</p>"
            self.send_page(400, page("URL 단축기", form_html(msg)))
            return
        except OverflowError as e:
            msg = f"<p class='err'>{escape(str(e))} (선형 탐지 테이블을 늘리지 않게 띄운 경우)</p>"
            self.send_page(507, page("URL 단축기", form_html(msg)))
            return
        link = f"{self.base_url()}/{code}"
        body = (f"<p>원래 주소: {escape(self.shortener.expand(code))}</p>"
                f"<p>짧은 링크: <a href='{escape(link)}'>{escape(link)}</a></p>"
                + form_html())
        self.send_page(200, page("줄였습니다", body))

    def log_message(self, fmt, *args):
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))


def make_server(port=8000, table="chaining", host="0.0.0.0", **table_options):
    table_cls = None
    for name, cls in TABLES:
        if name == table:
            table_cls = cls
    if table_cls is None:
        raise ValueError(f"모르는 테이블: {table}")
    handler = type("Handler", (ShortenerHandler,),
                   {"shortener": Shortener(table_cls=table_cls, **table_options),
                    "table_name": table})
    return ThreadingHTTPServer((host, port), handler)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--port", type=int, default=8000)
    p.add_argument("--table", choices=[name for name, _ in TABLES], default="chaining")
    p.add_argument("--capacity", type=int, help="처음 칸 수 M (예: 11)")
    p.add_argument("--max-load", help="이 적재율을 넘으면 늘림. none이면 늘리지 않음")
    args = p.parse_args()
    options = {}
    if args.capacity:
        options["capacity"] = args.capacity
    if args.max_load is not None:
        options["max_load"] = None if args.max_load.lower() == "none" else float(args.max_load)
    server = make_server(args.port, args.table, **options)
    print(f"http://localhost:{args.port} ({args.table})")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
