#!/usr/bin/env python3
"""
Dispatcher v2: drive the per-language drivers with `bench run_program`.

The driver prints K per-iteration microsecond timings to stdout, one per
line. Pilot takes each line as one reading, runs the driver again when its
output is used up, detects and drops the warm-up phase, and stops when the CI
is narrow enough or the per-cell session limit is reached.

The session runs at Pilot's default confidence level of 0.95 with a required
CI width of 10% of the mean (`--ci-perc 0.10`; the option takes a fraction).
After the session, the readings Pilot used (those after the last change-point)
are re-analysed with `bench analyze --cl 0.90`, with the autocorrelation limit
(0.1) that the session used, which gives the 90% interval that the report
quotes. Pilot's CI is the full width of the interval; the report quotes the
half-width (+/-) as a percentage of the mean.

Output: $BENCH_OUT/results.csv (default /tmp/bench_data/results.csv) with columns
   lang,algorithm,operation,bits,k_per_round,session_limit_s,rc,converged,
   readings,warmup_readings,mean_us,ci90_width_us,ci90_half_perc,
   ci95_width_us,session_s,wall_s
rc is Pilot's exit code: 0 when the session met its requirements, 13 when
the session limit was reached first.

Set PILOT_BENCH to override the path to the bench binary, JULIA to choose the
julia executable, BENCH_OUT to choose the output directory, and BENCH_LANGS
(python,julia) to run one language only. They default
to ../pilot-bench/build/cli/bench, julia, and /tmp/bench_data respectively.
"""
import os, signal, subprocess, sys, csv, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PY_REPO = ROOT if ROOT.endswith("-Python") else os.path.normpath(os.path.join(ROOT, "..", "Public-key-Cryptography-in-Python"))
JL_REPO = ROOT if ROOT.endswith("-Julia")  else os.path.normpath(os.path.join(ROOT, "..", "Public-key-Cryptography-in-Julia"))
PY    = os.path.join(PY_REPO, "bench", "py_bench.py")
JL    = os.path.join(JL_REPO, "bench", "jl_bench.jl")
BENCH = os.environ.get("PILOT_BENCH",
                       os.path.normpath(os.path.join(ROOT, "..", "pilot-bench", "build", "cli", "bench")))
JULIA = os.environ.get("JULIA", "julia")
OUT   = os.environ.get("BENCH_OUT", "/tmp/bench_data")
PILOT_OUT = os.path.join(OUT, "pilot_runs")
os.makedirs(PILOT_OUT, exist_ok=True)

ALGOS = ["rsa", "elgamal", "rabin", "paillier", "ss", "cocks"]
OPS   = ["keygen", "encrypt", "decrypt"]
BITS  = [512, 1024, 2048]
LANGS = os.environ.get("BENCH_LANGS", "python,julia").split(",")

# K = iterations per driver invocation. Goal: each round takes ~1–3 s of
# steady-state work, so pilot has many independent samples to assess the
# distribution including occasional GC pauses. The session limit caps the
# *total* wall pilot will spend on a cell — pilot exits early when CI is
# satisfied; this just bounds the pathological case.
def k_iters(op, bits):
    if op == "keygen":
        return {512: 20, 1024: 10, 2048: 5}[bits]
    return {512: 500, 1024: 200, 2048: 100}[bits]

# Python ElGamal and Rabin key generation at 2048 bits take several seconds
# per key; 120 s is not enough for them.
SESSION_LIMIT_OVERRIDE = {
    ("python", "elgamal", "keygen", 2048): 600,
    ("python", "rabin",   "keygen", 2048): 600,
}

def session_limit(lang, alg, op, bits):
    if (lang, alg, op, bits) in SESSION_LIMIT_OVERRIDE:
        return SESSION_LIMIT_OVERRIDE[(lang, alg, op, bits)]
    # Big enough that pilot can do several rounds even with Julia startup.
    # Slow ops need more wall to even reach a single round.
    if op == "keygen":
        return {512: 30, 1024: 60, 2048: 120}[bits]
    return {512: 30, 1024: 30, 2048: 60}[bits]

def run_pilot(lang, alg, op, bits, k, sess_limit):
    if lang == "python":
        prog = ["python3", PY, alg, op, str(bits), str(k)]
    else:
        prog = [JULIA, "--startup-file=no", JL, alg, op, str(bits), str(k)]
    out_dir = os.path.join(PILOT_OUT, f"{lang}_{alg}_{op}_{bits}")
    cmd = [BENCH, "run_program",
           "--pi", "lat,us,0,0,1",
           "--ci-perc", "0.10",   # a fraction of the mean: 0.10 is 10%
           "--preset", "quick",
           "-q",
           "--session-limit", str(sess_limit),
           "-o", out_dir,
           "--"] + prog
    # Pilot runs in a process group of its own. When the session ends, Pilot
    # sends SIGTERM to the driver and exits; a Julia driver can survive that
    # (sleeping, or spinning on the CPU), holding Pilot's stderr open and
    # competing with the next cell. So stdout and stderr go to files, and
    # whatever is left in the group is killed once Pilot has exited.
    os.makedirs(out_dir, exist_ok=True)
    so_path = os.path.join(out_dir, "pilot_stdout.txt")
    se_path = os.path.join(out_dir, "pilot_stderr.txt")
    with open(so_path, "w") as so, open(se_path, "w") as se:
        proc = subprocess.Popen(cmd, stdout=so, stderr=se, start_new_session=True)
        try:
            # Pilot checks the session limit between readings; the driver can
            # run for a while after that, so the timeout here is only a guard.
            rc = proc.wait(timeout=sess_limit + 600)
        finally:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            proc.wait()
    with open(so_path) as f:
        out = f.read()
    with open(se_path) as f:
        err = f.read()
    return subprocess.CompletedProcess(cmd, rc, out, err), out_dir

def load_readings(out_dir):
    xs = []
    with open(os.path.join(out_dir, "readings.csv")) as f:
        next(f)
        for line in f:
            parts = line.strip().split(",")
            if len(parts) >= 3 and parts[2] != "":
                xs.append(float(parts[2]))
    return xs

def analyze(out_dir, readings, cl):
    """Run `bench analyze` on the readings Pilot used; return (mean, ci_width)."""
    path = os.path.join(out_dir, "used_readings.txt")
    with open(path, "w") as f:
        f.write("\n".join(repr(x) for x in readings) + "\n")
    # The session chooses the subsession size with an autocorrelation limit
    # of 0.1 whatever the preset says (pilot_optimal_sample_size() is called
    # with its default limit), so the re-analysis uses 0.1 as well.
    p = subprocess.run([BENCH, "analyze", "-q", "-a", "0.1", "--cl", str(cl), path],
                       capture_output=True, text=True)
    vals = {}
    for line in p.stdout.splitlines():
        parts = line.split()
        if len(parts) == 2:
            vals[parts[0]] = parts[1]
    return float(vals.get("mean", "nan")), float(vals.get("CI", "nan"))

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
    total = len(ALGOS) * len(OPS) * len(BITS) * len(LANGS)
    i = 0
    t_start = time.time()
    header = ["lang", "algorithm", "operation", "bits", "k_per_round", "session_limit_s",
              "rc", "converged", "readings", "warmup_readings", "mean_us",
              "ci90_width_us", "ci90_half_perc", "ci95_width_us", "session_s", "wall_s"]
    for lang in LANGS:
        for alg in ALGOS:
            for op in OPS:
                for bits in BITS:
                    i += 1
                    k = k_iters(op, bits)
                    sl = session_limit(lang, alg, op, bits)
                    label = f"{lang}/{alg}/{op}/{bits}"
                    print(f"[{i:3d}/{total}] {label:36s} k={k:>4} sl={sl:>3}s ", end="", flush=True)
                    t0 = time.time()
                    nan_row = [lang, alg, op, bits, k, sl]
                    try:
                        p, out_dir = run_pilot(lang, alg, op, bits, k, sl)
                    except subprocess.TimeoutExpired:
                        print("TIMEOUT", flush=True)
                        rows.append(nan_row + ["timeout", 0] + ["nan"] * 7 + [f"{time.time() - t0:.1f}"])
                        continue
                    elapsed = time.time() - t0
                    parsed = parse_pilot_csv(p.stdout)
                    if not parsed or parsed.get("readings_mean_formatted", "") == "":
                        print(f"NO DATA  rc={p.returncode}  stderr={p.stderr[:80]}", flush=True)
                        rows.append(nan_row + [p.returncode, 0] + ["nan"] * 7 + [f"{elapsed:.1f}"])
                        continue
                    mean  = float(parsed["readings_mean_formatted"])
                    ci95  = float(parsed["readings_optimal_subsession_ci_width_formatted"])
                    begin = int(parsed["readings_dominant_segment_begin"])
                    sess  = float(parsed["session_duration"])
                    used  = load_readings(out_dir)[begin:]
                    m90, ci90 = analyze(out_dir, used, 0.90)
                    m95, a95  = analyze(out_dir, used, 0.95)
                    # The re-analysis must agree with the session's own result.
                    for what, a, b in (("mean", m90, mean), ("ci95", a95, ci95)):
                        if not (abs(a - b) <= 1e-4 * abs(b) + 1e-9):
                            print(f"\n    WARNING: analyze {what} {a} != session {b}", end="")
                    half_perc = 100.0 * (ci90 / 2) / mean if mean > 0 else float("nan")
                    conv = 1 if p.returncode == 0 else 0
                    print(f"rc={p.returncode:>2} n={len(used):>5} mean={mean:12.2f}us  "
                          f"+/-{half_perc:5.1f}% (90%)  sess={sess:6.1f}s  wall={elapsed:6.1f}s", flush=True)
                    rows.append([lang, alg, op, bits, k, sl, p.returncode, conv, len(used), begin,
                                 f"{mean:.6g}", f"{ci90:.6g}", f"{half_perc:.2f}", f"{ci95:.6g}",
                                 f"{sess:.2f}", f"{elapsed:.1f}"])
                    # Write after every cell so that a partial sweep is kept.
                    with open(os.path.join(OUT, "results.csv"), "w", newline="") as f:
                        w = csv.writer(f)
                        w.writerow(header)
                        w.writerows(rows)

    out_csv = os.path.join(OUT, "results.csv")
    with open(out_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(f"\nTotal wall: {time.time() - t_start:.1f}s. Wrote {out_csv}")

if __name__ == "__main__":
    main()
