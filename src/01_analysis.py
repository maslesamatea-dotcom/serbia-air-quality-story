"""Osnovna analiza PM10 po stanicama: dani iznad limita, vikend efekat i sezonalnost (iste mjere kao na interaktivnoj stranici)."""
import numpy as np, pandas as pd

LIMIT = 50                                        # dnevni limit PM10 (ug/m3)
df = pd.read_csv("data/pm10_dnevno_2022_2024.csv", parse_dates=["date"]).set_index("date")
long = df.reset_index().melt(id_vars="date", var_name="stanica", value_name="pm10").dropna()

# 1) dani iznad limita po stanici i godini
g = long.assign(godina=long["date"].dt.year, iznad=long["pm10"] > LIMIT).groupby(["stanica", "godina"])
rang = g.agg(dana_iznad=("iznad", "sum"), dana_mjerenja=("pm10", "size"), prosjek=("pm10", "mean")).reset_index()
rang["prosjek"] = rang["prosjek"].round(1)
rang.to_csv("results/rang_dani_iznad_limita.csv", index=False)

# 2) vikend naspram radnog dana, samo novembar-februar (grijna sezona)
w = long[long["date"].dt.month.isin([11, 12, 1, 2])].copy()
w["vikend"] = w["date"].dt.dayofweek >= 5
m = w.groupby(["stanica", "vikend"])["pm10"].mean().unstack()
vik = pd.DataFrame({"stanica": m.index, "radni": m[False].round(1).values, "vikend": m[True].round(1).values})
vik["razlika_pct"] = ((1 - m[True] / m[False]) * 100).round().astype(int).values
vik.to_csv("results/vikend_razlika.csv", index=False)

# 3) udio mjerenja iznad limita po mjesecu (sve stanice i godine zajedno)
mj = long.assign(mjesec=long["date"].dt.month, iznad=long["pm10"] > LIMIT).groupby("mjesec").agg(
    udio_iznad_pct=("iznad", lambda s: round(100 * s.mean())), mjerenja=("pm10", "size")).reset_index()
mj.to_csv("results/mjeseci_udio_iznad.csv", index=False)

top = rang[rang.godina == 2024].sort_values("dana_iznad", ascending=False)
print("2024, najvise dana iznad limita:", top.iloc[0].stanica, int(top.iloc[0].dana_iznad), "| najmanje:", top.iloc[-1].stanica, int(top.iloc[-1].dana_iznad))
print("vikend razlika, najveca:", vik.sort_values("razlika_pct").iloc[-1].stanica, int(vik.razlika_pct.max()), "% | najmanja:", vik.sort_values("razlika_pct").iloc[0].stanica, int(vik.razlika_pct.min()), "%")
