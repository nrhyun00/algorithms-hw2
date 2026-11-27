"""개별 체이닝과 선형 탐지의 탐색 비용 비교 (과제).

같은 칸 수 M = 4093, 같은 키, 크기 조정 없음(max_load=None).
적재율 α = 0.1 ~ 0.9 에서
  - 체이닝: 비교한 노드 수
  - 선형 탐지: 들여다본 칸 수 (실패 탐색은 멈춘 빈 칸까지 센다)
의 평균을 성공·실패 탐색으로 나눠 잰다. 같은 α에서 두 테이블에 똑같은 키를 넣고,
실패 탐색에도 똑같은 없는 키 MISSES개를 쓴다. 이것을 매번 다른 무작위 키로
TRIALS번 반복해 평균을 낸다 (α가 클수록 한 번 측정은 크게 흔들린다).

이론값
  체이닝     성공 ≈ 1 + α/2              실패 ≈ α
  선형 탐지  성공 ≈ (1 + 1/(1−α)) / 2    실패 ≈ (1 + 1/(1−α)²) / 2
"""

import csv
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src"))
sys.path.insert(0, HERE)

from hash_table import HashTable  # noqa: E402
from probing_table import LinearProbingTable  # noqa: E402
from probe_experiment import unique_urls  # noqa: E402
from svgplot import line_chart  # noqa: E402

M = 4093
MISSES = 2000
SEED = 2026
ALPHAS = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
TRIALS = 10


def theory(a):
    return {
        "chain_hit_theory": 1 + a / 2,
        "chain_miss_theory": a,
        "probe_hit_theory": (1 + 1 / (1 - a)) / 2,
        "probe_miss_theory": (1 + 1 / (1 - a) ** 2) / 2,
    }


def measure(table, keys, misses):
    for k in keys:
        table.put(k, True)
    hit = sum(table.find(k)[2] for k in keys) / len(keys)
    miss = sum(table.find(k)[2] for k in misses) / len(misses)
    return hit, miss


def main():
    rows = []
    for a in ALPHAS:
        n = round(a * M)
        sums = [0.0, 0.0, 0.0, 0.0]
        probe_miss_runs = []
        for trial in range(TRIALS):
            rng = random.Random(SEED + trial)
            keys = unique_urls(rng, n)
            present = HashTable(capacity=2 * n + 1)
            for k in keys:
                present.put(k, True)
            misses = unique_urls(rng, MISSES, avoid=present)
            ch, cm = measure(HashTable(capacity=M, max_load=None), keys, misses)
            ph, pm = measure(LinearProbingTable(capacity=M, max_load=None), keys, misses)
            for i, v in enumerate((ch, cm, ph, pm)):
                sums[i] += v
            probe_miss_runs.append(pm)
        ch, cm, ph, pm = (v / TRIALS for v in sums)
        row = {"alpha": a, "n": n,
               "chain_hit": ch, "chain_miss": cm,
               "probe_hit": ph, "probe_miss": pm,
               "probe_miss_min": min(probe_miss_runs), "probe_miss_max": max(probe_miss_runs)}
        row.update(theory(n / M))
        rows.append({k: (round(v, 4) if isinstance(v, float) else v) for k, v in row.items()})

    fields = ["alpha", "n",
              "chain_hit", "chain_hit_theory", "chain_miss", "chain_miss_theory",
              "probe_hit", "probe_hit_theory", "probe_miss", "probe_miss_theory",
              "probe_miss_min", "probe_miss_max"]
    with open(os.path.join(HERE, "compare.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    print(f"M = {M}, 실패 탐색 {MISSES}회, 같은 키로 두 방식 측정, {TRIALS}번 평균")
    print(f"{'α':>4} {'n':>5} | {'체인성공':>7} {'이론':>6} {'체인실패':>7} {'이론':>6} |"
          f" {'선형성공':>7} {'이론':>6} {'선형실패':>7} {'이론':>7}")
    for r in rows:
        print(f"{r['alpha']:>4} {r['n']:>5} | {r['chain_hit']:>7.3f} {r['chain_hit_theory']:>6.3f}"
              f" {r['chain_miss']:>7.3f} {r['chain_miss_theory']:>6.3f} |"
              f" {r['probe_hit']:>7.3f} {r['probe_hit_theory']:>6.3f}"
              f" {r['probe_miss']:>7.3f} {r['probe_miss_theory']:>7.3f}"
              f"  (선형 실패 {r['probe_miss_min']:.1f}~{r['probe_miss_max']:.1f})")

    xs = [r["alpha"] for r in rows]
    for kind, label in (("hit", "성공"), ("miss", "실패")):
        line_chart(
            os.path.join(HERE, f"compare-{kind}.svg"),
            f"{label} 탐색 비용: 체이닝 vs 선형 탐지 (M = {M}, {TRIALS}회 평균)",
            "적재율 α", "평균 탐색 비용 (노드 / 칸)", xs,
            [
                ("체이닝 (측정)", [r[f"chain_{kind}"] for r in rows], False),
                ("체이닝 (이론)", [r[f"chain_{kind}_theory"] for r in rows], True),
                ("선형 탐지 (측정)", [r[f"probe_{kind}"] for r in rows], False),
                ("선형 탐지 (이론)", [r[f"probe_{kind}_theory"] for r in rows], True),
            ],
        )
    print("저장: experiments/compare.csv, experiments/compare-hit.svg, experiments/compare-miss.svg")


if __name__ == "__main__":
    main()
