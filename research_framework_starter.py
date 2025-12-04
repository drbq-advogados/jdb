"""
research_framework_starter.py

Starter framework (self-contained single-file) for reproducible analysis of
random number generators and simple game-simulations. Designed to be:
- funcional (run directly),
- prático (CLI + functions),
- simples e autoexplicativo (docstrings + exemplos)

How to use (quick):
1. Create a virtualenv and install dependencies:
   python -m venv venv
   source venv/bin/activate   # on Windows: venv\\Scripts\\activate
   pip install -r requirements.txt

2. Run demo:
   python research_framework_starter.py demo

3. See help with commands:
   python research_framework_starter.py --help

Requirements (put this in requirements.txt):
numpy
pandas
scipy
matplotlib
statsmodels
joblib

This file includes the following features:
- Simuladores: LCG (toy), Mersenne Twister (numpy), TRNG simulated via os.urandom
- Testes estatísticos: chi-square, runs test, KS, autocorrelação
- Simulações Monte Carlo de apostas (modelo educativo)
- Geração de gráficos simples e relatórios em CSV
- CLI simples (argparse)

IMPORTANTE: este código foi feito para fins de pesquisa/educação. NÃO deve ser
usado para fraudar ou atacar sistemas reais. Se você fornecer dados reais,
certifique-se de ter autorização legal e anonimização.

"""

import argparse
import os
import json
from math import sqrt

import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
from joblib import Parallel, delayed


# ------------------------- Utility functions -------------------------

def ensure_output_dir(path="output"):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
    return path


def save_csv(data, path):
    """Save data (dict or array-like) to CSV. Ensures directory exists."""
    ensure_output_dir(os.path.dirname(path) or '.')
    pd.DataFrame(data).to_csv(path, index=False)


# ------------------------- RNG implementations -------------------------

def lcg(a, c, m, seed, n):
    """Generate n values from a simple Linear Congruential Generator (LCG).
    Returns numpy array of integers in [0, m).

    This is a toy LCG for experimentation only.
    """
    xs = np.empty(n, dtype=np.int64)
    x = int(seed)
    for i in range(n):
        x = (a * x + c) % m
        xs[i] = x
    return xs


def mt19937(n, seed=None):
    """Mersenne Twister via NumPy Generator.
    Returns values in range [0, 2**32) as int64.
    """
    rng = np.random.default_rng(seed)
    return rng.integers(0, 2**32, size=n, dtype=np.int64)


def trng_simulated(n):
    """Simulate a TRNG by drawing bytes from os.urandom and interpreting them.
    This is illustrative — real TRNGs are device-dependent.
    """
    b = os.urandom(n * 4)
    arr = np.frombuffer(b, dtype=np.uint32).astype(np.int64)
    return arr


# ------------------------- Statistical tests -------------------------

def chi_square_uniform_test(values, num_bins=None, max_bins=1024):
    """Chi-square test for (approximate) uniformity over discrete bins.

    This function is robust to large-support generators (e.g., 2**16 values).
    It will choose a sensible number of bins if num_bins is None.

    Args:
        values: integer array-like of draws
        num_bins: desired number of bins (optional). If larger than support,
                  it's reduced. If None, a heuristic is used.
        max_bins: safety cap on bins to avoid extremely large chi-square vectors.

    Returns:
        dict with chi2, p_value, counts (numpy array), expected
    """
    vals = np.asarray(values, dtype=np.int64)
    if vals.size == 0:
        raise ValueError("Empty values array")

    support = int(vals.max()) + 1

    if num_bins is None:
        # heuristic: min(256, sqrt(N), support)
        heuristic = int(min(256, max(2, int(np.sqrt(len(vals))))))
        num_bins = min(heuristic, support, max_bins)
    else:
        num_bins = int(min(num_bins, support, max_bins))

    # Compute histogram bins over the support range to ensure compatibility
    counts, bin_edges = np.histogram(vals, bins=num_bins, range=(0, support))
    expected = len(vals) / counts.size

    # SciPy requires matching shapes
    chi2_stat, p_value = stats.chisquare(counts, f_exp=np.full(counts.size, expected))
    return {"chi2": float(chi2_stat), "p_value": float(p_value), "counts": counts, "expected": expected}


def runs_test(values):
    """Runs test for randomness on binary sequence. We convert by median.
    Returns z-statistic and p-value (two-sided).
    """
    vals = np.asarray(values)
    med = np.median(vals)
    binary = (vals > med).astype(int)
    n1 = int(binary.sum())
    n2 = int(len(binary) - n1)
    if n1 == 0 or n2 == 0 or (n1 + n2) < 2:
        return {"z": 0.0, "p": 1.0}
    runs = 1 + int(np.sum(binary[1:] != binary[:-1]))
    expected_runs = 1 + 2.0 * n1 * n2 / (n1 + n2)
    var_runs = (2.0 * n1 * n2 * (2 * n1 * n2 - n1 - n2)) / (((n1 + n2) ** 2) * (n1 + n2 - 1))
    if var_runs <= 0:
        return {"z": 0.0, "p": 1.0}
    z = (runs - expected_runs) / sqrt(var_runs)
    p = 2 * (1 - stats.norm.cdf(abs(z)))
    return {"z": float(z), "p": float(p), "runs": int(runs), "n1": n1, "n2": n2}


def ks_test_uniform(values, low=0.0, high=1.0):
    """Kolmogorov-Smirnov test for uniformity on normalized floats in [0,1].
    If values are integers, caller should normalize them (divide by support-1).
    """
    u = np.asarray(values, dtype=float)
    # Map to [0,1] safely
    if u.max() > 1.0 or u.min() < 0.0:
        u = (u - u.min()) / (u.max() - u.min())
    res = stats.kstest(u, 'uniform')
    return {"stat": float(res.statistic), "p": float(res.pvalue)}


def autocorrelation(values, lag=1):
    """Simple lag-k autocorrelation for a numeric series.
    Returns Pearson correlation between series[:-lag] and series[lag:].
    """
    v = np.asarray(values, dtype=float)
    if lag >= len(v):
        return 0.0
    a = v[:-lag]
    b = v[lag:]
    if a.std() == 0 or b.std() == 0:
        return 0.0
    return float(np.corrcoef(a, b)[0, 1])


# ------------------------- Simulations & Monte Carlo -------------------------

def simulate_bets_uniform(draws, bet_number, payout, stake=1.0):
    """Simulate a simple repeated-bet strategy: bet always on bet_number.
    draws: array of integer results in [0, n_numbers)
    payout: multiplier for a win (e.g., 18)
    stake: amount staked each round
    Returns array of running balance
    """
    draws = np.asarray(draws, dtype=np.int64)
    n_numbers = int(draws.max()) + 1
    balance = 0.0
    history = []
    for d in draws:
        if d == bet_number:
            balance += payout * stake
        else:
            balance -= stake
        history.append(balance)
    return np.array(history)


def monte_carlo_final_balances(rng_func, rng_args=None, n_rounds=1000, n_sims=2000, payout=18.0, bet_number=0):
    """Parallel Monte Carlo: run n_sims simulations each with n_rounds draws.
    rng_func: function producing an array of length n_rounds
    rng_args: dict arguments for rng_func
    Returns numpy array of final balances (length n_sims)
    """
    if rng_args is None:
        rng_args = {}

    def one_sim(_):
        draws = rng_func(n_rounds, **rng_args) if 'n' not in rng_args else rng_func(**rng_args)
        # reduce draws to a small modulo if support is huge to speed sim
        mod = int(draws.max()) + 1
        if mod > 1000:
            # map into 0..999 to keep simulations fast while preserving uniformity
            draws_mod = draws % 1000
        else:
            draws_mod = draws
        hist = simulate_bets_uniform(draws_mod, bet_number=bet_number, payout=payout)
        return hist[-1]

    cores = max(1, os.cpu_count() - 1)
    results = Parallel(n_jobs=cores)(delayed(one_sim)(i) for i in range(n_sims))
    return np.array(results)


# ------------------------- Visualization & Reports -------------------------

def plot_histogram(values, title="Histogram", bins=50, savepath=None):
    plt.figure(figsize=(8,4))
    plt.hist(values, bins=bins)
    plt.title(title)
    plt.tight_layout()
    if savepath:
        ensure_output_dir(os.path.dirname(savepath) or '.')
        plt.savefig(savepath)
        plt.close()
    else:
        plt.show()


def plot_time_series(series, title="Series", savepath=None):
    plt.figure(figsize=(10,4))
    plt.plot(series)
    plt.title(title)
    plt.tight_layout()
    if savepath:
        ensure_output_dir(os.path.dirname(savepath) or '.')
        plt.savefig(savepath)
        plt.close()
    else:
        plt.show()


# ------------------------- Demo / Example pipeline -------------------------

def demo_workflow(output_dir="output"):
    out = ensure_output_dir(output_dir)
    print("[demo] Generating MT draws (10000) and LCG draws (10000)")
    mt = mt19937(10000, seed=12345)
    l = lcg(a=1103515245, c=12345, m=2**16, seed=42, n=10000)

    print("[demo] Running chi-square on LCG (m=2**16):")
    chi = chi_square_uniform_test(l, num_bins=None)
    # bin to sensible number automatically
    print(json.dumps({"chi2":chi["chi2"], "p":chi["p_value"]}, indent=2))

    print("[demo] Runs test on MT:")
    r = runs_test(mt)
    print(r)

    print("[demo] Autocorrelation lag1 (LCG):", autocorrelation(l, lag=1))

    print("[demo] Monte Carlo: simulate final balances with MT as source")
    finals = monte_carlo_final_balances(lambda n: mt19937(n, seed=None), {}, n_rounds=500, n_sims=500, payout=18.0)
    print("MC final balances summary:")
    print(pd.Series(finals).describe())

    # plots
    plot_histogram(finals, title="Monte Carlo final balances (demo)", savepath=os.path.join(out, 'mc_final_balances_hist.png'))
    plot_time_series(simulate_bets_uniform(mt % 25, bet_number=0, payout=18.0), title="Running balance (demo)", savepath=os.path.join(out, 'running_balance_demo.png'))

    # save results
    save_csv({"final_balances": finals}, os.path.join(out, 'mc_final_balances.csv'))
    print(f"[demo] Outputs saved to {out}")


# ------------------------- CLI -------------------------

def main():
    p = argparse.ArgumentParser(description="Starter research framework CLI")
    sub = p.add_subparsers(dest='cmd')

    sub.add_parser('demo', help='Run demo workflow (quick).')

    gen = sub.add_parser('gen', help='Generate draws from an RNG')
    gen.add_argument('--type', choices=['mt','lcg','trng'], default='mt')
    gen.add_argument('--n', type=int, default=10000)
    gen.add_argument('--out', default='output/draws.csv')
    gen.add_argument('--seed', type=int, default=123)

    chi = sub.add_parser('chi', help='Run chi-square on a CSV of integer draws')
    chi.add_argument('csvfile')
    chi.add_argument('--bins', type=int, default=None)

    mc = sub.add_parser('mc', help='Run a short Monte Carlo experiment')
    mc.add_argument('--source', choices=['mt','lcg'], default='mt')
    mc.add_argument('--n_rounds', type=int, default=1000)
    mc.add_argument('--n_sims', type=int, default=200)
    mc.add_argument('--payout', type=float, default=18.0)

    args = p.parse_args()

    if args.cmd == 'demo':
        demo_workflow(output_dir='output')
        return

    if args.cmd == 'gen':
        if args.type == 'mt':
            arr = mt19937(args.n, seed=args.seed)
        elif args.type == 'lcg':
            arr = lcg(a=1103515245, c=12345, m=2**16, seed=args.seed, n=args.n)
        else:
            arr = trng_simulated(args.n)
        df = pd.DataFrame({'draw': arr})
        ensure_output_dir(os.path.dirname(args.out) or '.')
        df.to_csv(args.out, index=False)
        print(f"Wrote {len(arr)} draws to {args.out}")
        return

    if args.cmd == 'chi':
        df = pd.read_csv(args.csvfile)
        values = df.iloc[:,0].astype(int).values
        res = chi_square_uniform_test(values, num_bins=args.bins)
        print(json.dumps({"chi2":res['chi2'], "p":res['p_value']}, indent=2))
        return

    if args.cmd == 'mc':
        if args.source == 'mt':
            rng = lambda n: mt19937(n, seed=None)
            rng_args = {}
        else:
            rng = lambda n: lcg(a=1103515245, c=12345, m=2**16, seed=np.random.randint(0,2**16), n=n)
            rng_args = {}
        finals = monte_carlo_final_balances(rng, rng_args, n_rounds=args.n_rounds, n_sims=args.n_sims, payout=args.payout)
        print(pd.Series(finals).describe())
        plot_histogram(finals, title='MC final balances', savepath='output/mc_final_balances.png')
        save_csv({'final_balances': finals.tolist()}, 'output/mc_final_balances.csv')
        print('Saved results to output/')
        return

    p.print_help()


if __name__ == '__main__':
    main()
