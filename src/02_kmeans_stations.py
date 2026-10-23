"""Grupisanje mjernih stanica PM10 prema obliku godisnjeg ciklusa (K-Means, k = 2) uz provjeru stabilnosti."""
import numpy as np, pandas as pd, warnings, itertools
warnings.filterwarnings("ignore")
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics import silhouette_score, adjusted_rand_score

SRC = "data/pm10_dnevno_2022_2024.csv"
OUT = "results/"
df = pd.read_csv(SRC, parse_dates=["date"]).set_index("date")
st = list(df.columns)
A, B = "Izraženo zimska", "Ujednačenija"

def features(d):
    """12 relativnih mjesecnih prosjeka (oblik sezone), omjer zima/ljeto, vikend efekat, log nivoa."""
    rows = {}
    for s in st:
        x = d[s].dropna()
        m = x.groupby(x.index.month).agg(["mean", "count"]).reindex(range(1, 13))
        m.loc[m["count"] < 15, "mean"] = np.nan               # mjesec sa manje od 15 dana ne racunamo
        mm = m["mean"].interpolate(limit_direction="both")
        rel = (mm / mm.mean()).values
        winter = x[x.index.month.isin([12, 1, 2])].mean(); summer = x[x.index.month.isin([6, 7, 8])].mean()
        w = x[x.index.month.isin([11, 12, 1, 2])]
        wk = 1 - w[w.index.dayofweek >= 5].mean() / w[w.index.dayofweek < 5].mean()
        rows[s] = list(rel) + [winter / summer, wk, np.log(x.mean())]
    cols = [f"m{i}" for i in range(1, 13)] + ["zima_ljeto", "vikend", "log_nivo"]
    return pd.DataFrame(rows, index=cols).T

def km2(F):
    Z = StandardScaler().fit_transform(F)
    lab = KMeans(n_clusters=2, n_init=50, random_state=0).fit_predict(Z)
    # grupa A = ona sa vecim prosjecnim omjerom zima/ljeto (oznake K-Means-a su proizvoljne)
    if F["zima_ljeto"][lab == 1].mean() < F["zima_ljeto"][lab == 0].mean(): lab = 1 - lab
    return lab, Z                                              # 1 = izrazeno zimska (A), 0 = ujednacenija (B)

F = features(df)
lab, Z = km2(F)
sil = silhouette_score(Z, lab)
ward = AgglomerativeClustering(n_clusters=2, linkage="ward").fit_predict(Z)
ari_ward = adjusted_rand_score(lab, ward)

# stabilnost po godinama
yl = {}
for y in (2022, 2023, 2024):
    yl[y] = km2(features(df[df.index.year == y]))[0]
ari_pairs = [adjusted_rand_score(yl[a], yl[b]) for a, b in itertools.combinations(yl, 2)]
same = sum((yl[y] == lab).astype(int) for y in yl)             # u koliko od 3 godine ista grupa kao u ukupnom rjesenju

# tabele za stranicu
t = pd.DataFrame({
    "stanica": st, "grupa": [A if l == 1 else B for l in lab],
    "zima_ljeto": F["zima_ljeto"].round(1).values, "prosjek_pm10": np.exp(F["log_nivo"]).round(1).values,
    "vikend_pct": (100 * F["vikend"]).round(0).astype(int).values, "godina_u_grupi": np.asarray(same)})
t.sort_values(["grupa", "zima_ljeto"], ascending=[True, False]).to_csv(OUT + "klasteri_stanice.csv", index=False, encoding="utf-8")

prof = []
for g, l in ((A, 1), (B, 0)):
    members = [s for s, k in zip(st, lab) if k == l]
    for i in range(1, 13):
        prof.append({"grupa": g, "mjesec": i, "relativni_prosjek": round(F.loc[members, f"m{i}"].mean(), 2), "broj_stanica": len(members)})
pd.DataFrame(prof).to_csv(OUT + "klasteri_profil.csv", index=False, encoding="utf-8")

kv = pd.DataFrame([
    {"mjera": "silhouette", "vrijednost": round(sil, 2)},
    {"mjera": "slaganje_sa_ward_ari", "vrijednost": round(ari_ward, 2)},
    {"mjera": "slaganje_izmedju_godina_ari", "vrijednost": round(float(np.mean(ari_pairs)), 2)}])
kv.to_csv(OUT + "klasteri_kvalitet.csv", index=False, encoding="utf-8")

if __name__ == "__main__":
    print(t.sort_values(["grupa", "zima_ljeto"], ascending=[True, False]).to_string(index=False))
    print("\n", pd.DataFrame(prof).pivot(index="mjesec", columns="grupa", values="relativni_prosjek").to_string())
    print("\n", kv.to_string(index=False))
    print("ARI parovi godina:", [round(a, 2) for a in ari_pairs])
