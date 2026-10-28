# How Serbia Breathes: Analysis and Clustering of PM10 Monitoring Stations

**Language:** English | [Srpski](README.sr.md)

An exploration of public air-quality data for Serbia: how many days each station exceeds the limit, how pollution changes over the year and the week, and which stations "breathe" in the same way (K-Means clustering).

Author: Matea Masleša

**Interactive page:** https://maslesamatea-dotcom.github.io/serbia-air-quality-story/ (in Serbian)

## Data

- Daily PM10 means (µg/m³) from **16 national-network stations**, 2022–2024. Source: Serbian Environmental Protection Agency (SEPA), via the open data portal data.gov.rs.
- The file `data/pm10_dnevno_2022_2024.csv` is merged from yearly files (the procedure is described in the repository *valjevo-air-quality-prediction*, script `01_prepare_data.py`). Check the licence of the SEPA datasets on the portal before reusing them.
- Daily limit used in the analysis: **50 µg/m³**.

## What was done

1. **Days above the limit** per station and year (`src/01_analysis.py`).
2. **Weekend vs weekday** in the heating season (November–February).
3. **Seasonality:** share of measurements above the limit by month.
4. **Station clustering** (`src/02_kmeans_stations.py`): K-Means with two clusters on 15 features per station (12 relative monthly means, winter-to-summer ratio, weekend difference, log of the average level), after standardisation. Cluster labels are aligned so that group A is the one with the higher winter-to-summer ratio.
5. **Cluster reliability checks:** silhouette score, comparison with hierarchical (Ward) clustering, and stability when each year is clustered separately (adjusted Rand index).

## Results

**Days above the limit, 2024**

![ranking](results/01_rang_stanica_2024.png)

- Most: **Popovac, 174 days**; fewest: **Beograd Zeleno brdo, 34 days**, i.e. about five times fewer.

**One station, one year**

![calendar](results/02_kalendar_valjevo_2024.png)

**Weekends are cleaner, but not everywhere**

![weekend](results/03_vikend_efekat.png)

- In winter months PM10 is **18%** lower on weekends in Valjevo and Popovac, but only **3%** lower in Beočin. The cause cannot be determined from these data.

**Seasonality**

![seasonality](results/04_sezonalnost.png)

- About **48%** of measurements were above the limit in December and **45%** in January, but only **2 to 5%** from May to August.

**Station groups**

![groups](results/05_grupe_stanica.png)

| Group | Stations | Winter/summer ratio (mean) |
|---|---|---|
| Strongly winter-peaked | 10 (Novi Pazar, Niš ×2, Valjevo, Pirot, Smederevo Centar, Čačak, Beograd Mostar, Užice, Obrenovac) | about 3 |
| More even through the year | 6 (Smederevo Radinac, Beograd ×3, Beočin, Popovac) | about 1.6 |

All numbers are in `results/`.

## How reliable is the clustering?

| Measure | Value | Meaning |
|---|---|---|
| Silhouette | 0.32 | weak to moderate separation of groups |
| Agreement with Ward clustering (ARI) | 1.00 | a second method gives the same assignment |
| Agreement between years (ARI, mean) | 0.30 | groups change partly from year to year |

The conclusion is that the split is usable, but the boundary between the groups is **soft**. The table `results/klasteri_stanice.csv` also has a column `godina_u_grupi` (in how many of the 3 years the station is in the same group as in the overall solution); the least stable station is Obrenovac Centar.

## Limitations

- Only **16 stations**, which is small for clustering, so the result is exploratory.
- Daily means hide short peaks within a day.
- Some days have no measurements. A month with fewer than 15 measured days is excluded from a station's profile, and rare gaps are filled from neighbouring months.
- The data do not show **why** a station has a given pattern (heating, industry, location), only how it behaves.
- One day above the limit is not the same as exceeding the annual permitted number of days.
- This is an analysis of public data, not a health assessment.

## Structure and usage

```
docs/      interactive page (index.html, published via GitHub Pages)
data/      pm10_dnevno_2022_2024.csv
src/       01_analysis.py, 02_kmeans_stations.py, 03_figures.py
results/   tables (csv) and figures (png)
```

```bash
pip install -r requirements.txt
python src/01_analysis.py
python src/02_kmeans_stations.py
python src/03_figures.py
```

Run the scripts in order from the repository root.

The interactive page (`docs/index.html`) is a standalone file that opens in a browser with no installation. It uses the [d3](https://d3js.org) library (ISC licence), which is included in the file. The page itself is in Serbian.
