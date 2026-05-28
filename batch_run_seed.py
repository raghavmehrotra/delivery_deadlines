from model import DeliveryModel
import matplotlib.pyplot as plt

N_STEPS = 960
N_SEEDS = 10
DEFAULTS = {"delivery_deadline": 20, "n_workers": 90, "speed_threshold": 1.5}

seeds, injuries, earnings = [], [], []
for s in range(N_SEEDS):
    model = DeliveryModel(seed=s, **DEFAULTS)
    for _ in range(N_STEPS):
        model.step()
    df = model.datacollector.get_model_vars_dataframe()
    seeds.append(s)
    injuries.append(df["n_injuries_total"].iloc[-1])
    earnings.append(df["avg_work_earnings"].iloc[-1])

mean_inj  = sum(injuries) / N_SEEDS
mean_earn = sum(earnings) / N_SEEDS

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4))
fig.suptitle("Stability Check — 10 Seeds, Default Parameters", fontsize=12)

ax1.plot(seeds, injuries, marker="o", color="tab:red")
ax1.axhline(mean_inj, linestyle="--", color="tab:red", alpha=0.5, label=f"mean={mean_inj:.0f}")
ax1.set_xlabel("Seed")
ax1.set_ylabel("Total Injuries")
ax1.set_xticks(seeds)
ax1.legend()

ax2.plot(seeds, earnings, marker="o", color="tab:green")
ax2.axhline(mean_earn, linestyle="--", color="tab:green", alpha=0.5, label=f"mean={mean_earn:.0f}")
ax2.set_xlabel("Seed")
ax2.set_ylabel("Avg Worker Earnings (INR)")
ax2.set_xticks(seeds)
ax2.legend()

plt.tight_layout()
plt.savefig("batch_seed_stability.png", dpi=150)
print("Saved batch_seed_stability.png")
