"""적재율에 따른 개별 체이닝의 탐색 비용 실험.

칸 수 M = 4093 고정, max_load=None(크기 조정 없음).
성공 탐색: 넣은 키를 모두 찾을 때 비교한 노드 수의 평균.
실패 탐색: 넣지 않은 키 MISSES개를 찾을 때 비교한 노드 수의 평균.
이론값: 성공 ≈ 1 + α/2, 실패 ≈ α.
"""

import csv
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src"))
sys.path.insert(0, HERE)

from hash_table import HashTable  # noqa: E402
from svgplot import line_chart  # noqa: E402

M = 4093
MISSES = 2000
SEED = 2026
ALPHAS = [0.25, 0.5, 1, 1.5, 2, 3, 4]
CHARS = "abcdefghijklmnopqrstuvwxyz0123456789"


def random_url(rng):
    path = "".join(rng.choice(CHARS) for _ in range(rng.randint(4, 12)))
    return f"https://example{rng.randint(1, 999)}.com/{path}"


def unique_urls(rng, count, avoid=None):
    seen = HashTable(capacity=2 * count + 1)
    out = []
    while len(out) < count:
        url = random_url(rng)
        if url in seen or (avoid is not None and url in avoid):
            continue
        seen.put(url, True)
        out.append(url)
    return out


def measure(alpha, rng):
    n = round(alpha * M)
    keys = unique_urls(rng, n)
    t = HashTable(capacity=M, max_load=None)
    for k in keys:
        t.put(k, True)
    hit = sum(t.find(k)[2] for k in keys) / n
    misses = unique_urls(rng, MISSES, avoid=t)
    miss = sum(t.find(k)[2] for k in misses) / MISSES
    return n, hit, miss


def main():
    rng = random.Random(SEED)
    rows = []
    for a in ALPHAS:
        n, hit, miss = measure(a, rng)
        actual = n / M
        rows.append({
            "alpha": a,
            "n": n,
            "hit": round(hit, 4),
            "hit_theory": round(1 + actual / 2, 4),
            "miss": round(miss, 4),
            "miss_theory": round(actual, 4),
        })

    with open(os.path.join(HERE, "results.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    print(f"개별 체이닝, M = {M}, 실패 탐색 {MISSES}회")
    print(f"{'α':>5} {'n':>6} {'성공':>8} {'이론':>8} {'실패':>8} {'이론':>8}")
    for r in rows:
        print(f"{r['alpha']:>5} {r['n']:>6} {r['hit']:>8.3f} {r['hit_theory']:>8.3f}"
              f" {r['miss']:>8.3f} {r['miss_theory']:>8.3f}")

    xs = [r["alpha"] for r in rows]
    line_chart(
        os.path.join(HERE, "probes.svg"),
        f"개별 체이닝: 적재율과 비교한 노드 수 (M = {M})",
        "적재율 α", "평균 비교 노드 수", xs,
        [
            ("성공 (측정)", [r["hit"] for r in rows], False),
            ("성공 (1 + α/2)", [r["hit_theory"] for r in rows], True),
            ("실패 (측정)", [r["miss"] for r in rows], False),
            ("실패 (α)", [r["miss_theory"] for r in rows], True),
        ],
    )
    print("저장: experiments/results.csv, experiments/probes.svg")


if __name__ == "__main__":
    main()
