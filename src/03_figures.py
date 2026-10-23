"""Staticni grafici za README (iste mjere kao interaktivna stranica)."""
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba

plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False, "figure.dpi": 130})
BLUE, ORANGE, RED = "#5b6ee1", "#e8681a", "#d6453d"
MJ = ["jan", "feb", "mar", "apr", "maj", "jun", "jul", "avg", "sep", "okt", "nov", "dec"]
df = pd.read_csv("data/pm10_dnevno_2022_2024.csv", parse_dates=["date"]).set_index("date")

# 1) rang stanica, 2024
r = pd.read_csv("results/rang_dani_iznad_limita.csv"); r = r[r.godina == 2024].sort_values("dana_iznad")
fig, ax = plt.subplots(figsize=(7, 5))
ax.barh(r.stanica, r.dana_iznad, color=[RED if i == len(r) - 1 else BLUE for i in range(len(r))], alpha=.85)
for y, v in enumerate(r.dana_iznad): ax.text(v + 2, y, int(v), va="center")
ax.set_xlabel("dana iznad limita od 50 µg/m³ (2024.)"); ax.set_title("Gdje je najteže disati"); fig.tight_layout()
fig.savefig("results/01_rang_stanica_2024.png"); plt.close()

# 2) kalendar jedne stanice
def calendar(station, year, fname):
    s = df[station]; s = s[s.index.year == year]
    full = pd.date_range(f"{year}-01-01", f"{year}-12-31"); s = s.reindex(full)
    off = full[0].dayofweek
    grid = np.full((7, 54), np.nan)
    for i, v in enumerate(s.values): grid[(i + off) % 7, (i + off) // 7] = v if not np.isnan(v) else -1
    def col(v):
        if np.isnan(v): return (1, 1, 1, 0)
        if v < 0: return to_rgba("#bbbbbb", .5)
        if v <= 25: return to_rgba(BLUE, .28)
        if v <= 50: return to_rgba(BLUE, .65)
        if v <= 100: return to_rgba(RED, .6)
        return to_rgba(RED, 1)
    img = np.array([[col(grid[i, j]) for j in range(54)] for i in range(7)])
    fig, ax = plt.subplots(figsize=(11, 2.4)); ax.imshow(img, aspect="equal", interpolation="nearest")
    ax.set_yticks([0, 2, 4, 6]); ax.set_yticklabels(["P", "S", "P", "N"])
    ticks = [((pd.Timestamp(f"{year}-{m:02d}-01") - full[0]).days + off) // 7 for m in range(1, 13)]
    ax.set_xticks(ticks); ax.set_xticklabels(MJ); ax.tick_params(length=0)
    for sp in ax.spines.values(): sp.set_visible(False)
    ax.set_title(f"{station}, {year}. (crveno = iznad limita)"); fig.tight_layout(); fig.savefig(fname); plt.close()
calendar("Valjevo", 2024, "results/02_kalendar_valjevo_2024.png")

# 3) vikend
v = pd.read_csv("results/vikend_razlika.csv").sort_values("razlika_pct")
fig, ax = plt.subplots(figsize=(7, 5)); ax.barh(v.stanica, v.razlika_pct, color=BLUE, alpha=.85)
for y, x in enumerate(v.razlika_pct): ax.text(x + .3, y, f"{x}%", va="center")
ax.set_xlabel("za koliko % je PM10 vikendom niži nego radnim danom (nov–feb)"); ax.set_title("Vikend je čistiji, ali ne svuda"); fig.tight_layout()
fig.savefig("results/03_vikend_efekat.png"); plt.close()

# 4) mjeseci
m = pd.read_csv("results/mjeseci_udio_iznad.csv")
fig, ax = plt.subplots(figsize=(7, 3.2)); ax.bar([MJ[i - 1] for i in m.mjesec], m.udio_iznad_pct, color=BLUE, alpha=.85)
for i, x in enumerate(m.udio_iznad_pct): ax.text(i, x + 1, f"{x}%", ha="center", fontsize=8)
ax.set_ylabel("% mjerenja iznad limita"); ax.set_title("Kada je vazduh najlošiji"); fig.tight_layout(); fig.savefig("results/04_sezonalnost.png"); plt.close()

# 5) grupe stanica
c = pd.read_csv("results/klasteri_stanice.csv"); p = pd.read_csv("results/klasteri_profil.csv")
col = {"Izraženo zimska": BLUE, "Ujednačenija": ORANGE}
fig, axs = plt.subplots(1, 2, figsize=(11, 4))
for g, d in c.groupby("grupa"): axs[0].scatter(d.zima_ljeto, d.prosjek_pm10, s=60, color=col[g], alpha=.85, label=g)
axs[0].set_xlabel("koliko je zima gora od ljeta (puta)"); axs[0].set_ylabel("prosječan PM10 (µg/m³)"); axs[0].legend(frameon=False)
for g, d in p.groupby("grupa"): axs[1].plot(d.mjesec, d.relativni_prosjek, marker="o", color=col[g], label=g)
axs[1].axhline(1, color="gray", ls="--", lw=1); axs[1].set_xticks(range(1, 13)); axs[1].set_xticklabels(MJ)
axs[1].set_ylabel("mjesečni prosjek / godišnji prosjek stanice"); axs[1].set_title("Godišnji ciklus po grupama")
axs[0].set_title("Grupe stanica (K-Means)"); fig.tight_layout(); fig.savefig("results/05_grupe_stanica.png"); plt.close()
print("grafici sacuvani")
