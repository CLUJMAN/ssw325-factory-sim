"""Run the factory under different configurations and compare results.

Usage:  python experiments.py
Saves experiment_results.csv, and experiment_results.png if matplotlib is installed.
"""
import contextlib
import csv
import io
import random

import simpy
from factory_controller import FactoryController

SIM_TIME = 8 * 60          # minutes per run (one shift)
REPLICATIONS = 5           # runs per configuration, averaged (different random seeds)

BASE = dict(num_chargers=24, num_benches=20, arrival_interval=1, base_travel_rate=0.2)

# each experiment changes one setting from BASE
EXPERIMENTS = {
    "arrival_interval": [1, 2, 3, 4, 5],
    "base_travel_rate": [0.05, 0.1, 0.2, 0.3],
    "num_chargers":     [12, 18, 24, 30, 36],
    "num_benches":      [10, 15, 20, 25, 30],
}

METRICS = ["throughput_per_hour", "avg_cycle_time", "arm_utilization",
           "charger_utilization", "bench_utilization", "idle_rack_size", "safety_violations"]


def run_once(config, seed):
    random.seed(seed)
    env = simpy.Environment()
    fc = FactoryController(env, **config)
    with contextlib.redirect_stdout(io.StringIO()):     # hide the per-event log
        fc.run(until=SIM_TIME)
    return fc.stats(SIM_TIME)


def run_config(config):
    results = [run_once(config, seed) for seed in range(REPLICATIONS)]
    return {m: sum(r[m] for r in results) / len(results) for m in METRICS}


def main():
    rows = []
    for param, values in EXPERIMENTS.items():
        print(f"\n=== Varying {param} (others: {BASE}) ===")
        print(f"{param:>18} | thru/hr | cycle min | arm util | chg util | bench util | rack left")
        for v in values:
            config = dict(BASE, **{param: v})
            avg = run_config(config)
            rows.append({"param": param, "value": v, **avg})
            print(f"{v:>18} | {avg['throughput_per_hour']:7.2f} | {avg['avg_cycle_time']:9.1f} |"
                  f" {avg['arm_utilization']:7.1%} | {avg['charger_utilization']:7.1%} |"
                  f" {avg['bench_utilization']:9.1%} | {avg['idle_rack_size']:9.1f}")

    with open("experiment_results.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["param", "value"] + METRICS)
        writer.writeheader()
        writer.writerows(rows)
    print("\nSaved experiment_results.csv")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed, skipping charts (pip install matplotlib)")
        return

    fig, axes = plt.subplots(2, 2, figsize=(11, 8))
    for ax, param in zip(axes.flat, EXPERIMENTS):
        pts = [r for r in rows if r["param"] == param]
        xs = [r["value"] for r in pts]
        ax.plot(xs, [r["throughput_per_hour"] for r in pts], marker="o", label="Throughput (devices/hr)")
        ax.set_xlabel(param)
        ax.set_ylabel("devices / hour")
        ax.set_ylim(bottom=0)
        ax2 = ax.twinx()
        ax2.plot(xs, [r["arm_utilization"] * 100 for r in pts], marker="s", linestyle="--",
                 color="tab:orange", label="Arm utilization (%)")
        ax2.set_ylabel("arm utilization %")
        ax2.set_ylim(0, 105)
        ax.set_title(f"Effect of {param}")
        ax.grid(alpha=0.3)
    h1, l1 = axes.flat[0].get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    fig.legend(h1 + h2, l1 + l2, loc="upper center", ncol=2)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig("experiment_results.png", dpi=150)
    print("Saved experiment_results.png")


if __name__ == "__main__":
    main()
