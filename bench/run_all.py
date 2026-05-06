#!/usr/bin/env python3
"""
Dispatcher v2: drive the per-language drivers with `bench run_program`.

Pilot keeps invoking the driver across multiple rounds until CI converges
or a per-cell session limit is reached. The driver prints K per-iteration
microsecond timings to stdout (one per line) — pilot consumes them as
multiple samples per round, automatically detects warmup, drops it, and
reports a converged mean ± CI.

Output: $BENCH_OUT/results.csv (default /tmp/bench_data/results.csv) with columns
   lang,algorithm,operation,bits,iters_per_round,mean_us,ci_us,ci_perc,session_s

Set PILOT_BENCH to override the path to the bench binary; set BENCH_OUT to
choose the output directory. Both default to ../pilot-bench/build/cli/bench
and /tmp/bench_data respectively.
"""
import os, subprocess, sys, csv, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PY_REPO = ROOT if ROOT.endswith("-Python") else os.path.normpath(os.path.join(ROOT, "..", "Public-key-Cryptography-in-Python"))
JL_REPO = ROOT if ROOT.endswith("-Julia")  else os.path.normpath(os.path.join(ROOT, "..", "Public-key-Cryptography-in-Julia"))
PY    = os.path.join(PY_REPO, "bench", "py_bench.py")
JL    = os.path.join(JL_REPO, "bench", "jl_bench.jl")
BENCH = os.environ.get("PILOT_BENCH",
                       os.path.normpath(os.path.join(ROOT, "..", "pilot-bench", "build", "cli", "bench")))
OUT   = os.environ.get("BENCH_OUT", "/tmp/bench_data")
PILOT_OUT = os.path.join(OUT, "pilot_runs")
os.makedirs(PILOT_OUT, exist_ok=True)

ALGOS = ["rsa", "elgamal", "rabin", "paillier", "ss", "cocks"]
OPS   = ["keygen", "encrypt", "decrypt"]
BITS  = [512, 1024, 2048]

# K = iterations per driver invocation. Goal: each round takes ~1–3 s of
# steady-state work, so pilot has many independent samples to assess the
# distribution including occasional GC pauses. The session limit caps the
# *total* wall pilot will spend on a cell — pilot exits early when CI is
# satisfied; this just bounds the pathological case.
def k_iters(op, bits):
    if op == "keygen":
        return {512: 20, 1024: 10, 2048: 5}[bits]
    return {512: 500, 1024: 200, 2048: 100}[bits]

def session_limit(op, bits):
    # Big enough that pilot can do several rounds even with Julia startup.
    # Slow ops need more wall to even reach a single round.
    if op == "keygen":
        return {512: 30, 1024: 60, 2048: 120}[bits]
    return {512: 30, 1024: 30, 2048: 60}[bits]

def run_pilot(lang, alg, op, bits, k, sess_limit):
    if lang == "python":
        prog = ["python3", PY, alg, op, str(bits), str(k)]
    else:
        prog = ["julia", "--startup-file=no", JL, alg, op, str(bits), str(k)]
    out_dir = os.path.join(PILOT_OUT, f"{lang}_{alg}_{op}_{bits}")
    cmd = [BENCH, "run_program",
           "--pi", "lat,us,0,0,1",
           "--ci-perc", "10",
           "--preset", "quick",
           "-q",
           "--session-limit", str(sess_limit),
           "-o", out_dir,
           "--"] + prog
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=sess_limit + 30)
    return p

def parse_pilot_csv(text):
    """Pilot prints a header then one data line. Return dict by header name."""
    lines = [l for l in text.splitlines() if l.strip() and not l.startswith("[")]
    if len(lines) < 2:
        return None
    keys = lines[0].split(",")
    vals = lines[1].split(",")
    if len(keys) != len(vals):
        return None
    return dict(zip(keys, vals))

def main():
    rows = []
    total = len(ALGOS) * len(OPS) * len(BITS) * 2
    i = 0
    t_start = time.time()
    for lang in ("python", "julia"):
        for alg in ALGOS:
            for op in OPS:
                for bits in BITS:
                    i += 1
                    k = k_iters(op, bits)
                    sl = session_limit(op, bits)
                    label = f"{lang}/{alg}/{op}/{bits}"
                    print(f"[{i:3d}/{total}] {label:36s} k={k:>4} sl={sl:>3}s ", end="", flush=True)
                    t0 = time.time()
                    try:
                        p = run_pilot(lang, alg, op, bits, k, sl)
                    except subprocess.TimeoutExpired:
                        print(f"TIMEOUT")
                        rows.append([lang, alg, op, bits, k, "nan", "nan", "nan", "nan"])
                        continue
                    parsed = parse_pilot_csv(p.stdout)
                    elapsed = time.time() - t0
                    if not parsed:
                        # pilot may have failed (rc 13 = session limit reached but data exists; print stderr)
                        print(f"NO DATA  rc={p.returncode}  stderr={p.stderr[:80]}")
                        rows.append([lang, alg, op, bits, k, "nan", "nan", "nan", f"{elapsed:.1f}"])
                        continue
                    try:
                        mean = float(parsed.get("readings_mean_formatted", "nan"))
                        ci   = float(parsed.get("readings_optimal_subsession_ci_width_formatted", "nan"))
                        sess = float(parsed.get("session_duration", "nan"))
                    except ValueError:
                        mean, ci, sess = float("nan"), float("nan"), float("nan")
                    ci_pct = (100.0 * ci / mean) if (mean and mean == mean and mean > 0) else float("nan")
                    print(f"mean={mean:9.2f}us  ±{ci_pct:5.1f}%  sess={sess:5.1f}s  wall={elapsed:5.1f}s")
                    rows.append([lang, alg, op, bits, k,
                                 f"{mean:.4f}", f"{ci:.4f}", f"{ci_pct:.2f}", f"{sess:.2f}"])

    out_csv = os.path.join(OUT, "results.csv")
    with open(out_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["lang", "algorithm", "operation", "bits", "k_per_round",
                    "mean_us", "ci_us", "ci_perc", "session_s"])
        w.writerows(rows)
    print(f"\nTotal wall: {time.time() - t_start:.1f}s. Wrote {out_csv}")

if __name__ == "__main__":
    main()
