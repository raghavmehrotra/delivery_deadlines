from model import DeliveryModel
import matplotlib.pyplot as plt

SEED = 42
N_STEPS = 960
DEFAULTS = {"delivery_deadline": 20, "n_workers": 90, "speed_threshold": 1.5}

SWEEPS = {
    "delivery_deadline": [10, 15, 20, 30, 40, 60],
    "n_workers":         [30, 60, 90, 120],
    "speed_threshold":   [1.0, 1.5, 2.0, 2.5, 3.0],
}


def run_one(delivery_deadline, n_workers, speed_threshold):
    model = DeliveryModel(
        seed=SEED,
        n_workers=n_workers,
        delivery_deadline=delivery_deadline,
        speed_threshold=speed_threshold,
    )
    for _ in range(N_STEPS):
        model.step()
    df = model.datacollector.get_model_vars_dataframe()
    return df["n_injuries_total"].iloc[-1], df["avg_work_earnings"].iloc[-1]


results = {}
for param, values in SWEEPS.items():
    injuries, earnings = [], []
    for v in values:
        kwargs = {**DEFAULTS, param: v}
        inj, earn = run_one(**kwargs)
        injuries.append(inj)
        earnings.append(earn)
    results[param] = {"values": values, "injuries": injuries, "earnings": earnings}

LABELS = {
    "delivery_deadline": "Delivery Deadline (steps)",
    "n_workers":         "Number of Workers",
    "speed_threshold":   "Speed Threshold (cells/step)",
}

fig, axes = plt.subplots(2, 3, figsize=(14, 8))
fig.suptitle("Quick Commerce Delivery ABM — Parameter Sweeps", fontsize=13)

for col, param in enumerate(SWEEPS):
    x = results[param]["values"]
    axes[0][col].plot(x, results[param]["injuries"], marker="o", color="tab:red")
    axes[0][col].set_title(LABELS[param])
    axes[0][col].set_ylabel("Total Injuries" if col == 0 else "")
    axes[0][col].set_xlabel(LABELS[param])

    axes[1][col].plot(x, results[param]["earnings"], marker="o", color="tab:green")
    axes[1][col].set_ylabel("Avg Worker Earnings (INR)" if col == 0 else "")
    axes[1][col].set_xlabel(LABELS[param])

plt.tight_layout()
plt.savefig("batch_results.png", dpi=150)
print("Saved batch_results.png")
