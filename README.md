# Urban Heat Island Explorer 🌡️

Predicting block-level surface temperature across **Lahore** and **Karachi** using satellite thermal imagery, vegetation and built-up indices, and street-level infrastructure data — with an interactive map that explains *why* each block is hot.

**[🔗 Live Demo](#)** — replace this with your GitHub Pages link once deployed

![Surface temperature range](https://img.shields.io/badge/R²-0.87–0.89-brightgreen) ![Cities](https://img.shields.io/badge/cities-Lahore%20%7C%20Karachi-blue) ![Grid resolution](https://img.shields.io/badge/resolution-500m-orange)

---

## What this is

Most urban heat maps stop at a static satellite picture. This project goes further: it fuses satellite thermal data with street-level features into a **500m × 500m grid**, trains a machine learning model to predict surface temperature from those features, and uses SHAP explainability to answer *"why is this specific block hot?"* — not just *"how hot is it?"*

The result is an interactive web map where clicking any block gives a plain-language breakdown of its heat drivers, similar to what an urban planner would want when deciding where to add green space or rethink construction materials.

## Key finding

The two cities are hot for **completely different reasons**:

| | Lahore (inland) | Karachi (coastal) |
|---|---|---|
| **Dominant driver** | Surface imperviousness (NDBI) — 81.5% | Elevation / distance to coast — 65%+ |
| **Model R²** | 0.871 | 0.894 |
| **Mean absolute error** | 0.76°C | 1.63°C |
| **Story** | Classic textbook urban heat island — concrete and built-up density drive heat | The Arabian Sea's cooling effect dominates over land-use patterns |

This makes sense once you think about it — but it's not something you'd know without actually modeling both cities and comparing feature importances directly.

## How it works

**1. Data collection** — Landsat 8 Collection 2 thermal imagery (30–100m resolution) pulled via Google Earth Engine, combined with OpenStreetMap road network data via `osmnx`.

**2. Feature engineering** — for every 500m grid cell:
- `NDBI` (Normalized Difference Built-up Index) — how concrete/built-up the area is
- `NDVI` (Normalized Difference Vegetation Index) — vegetation cover
- `Elevation` — from NASA SRTM
- `Road density` — total road length within the cell (OpenStreetMap)
- `Distance to coast` — for Karachi only, straight-line distance to the nearest coastline (OpenStreetMap)

**3. Modeling** — a Random Forest Regressor trained to predict Land Surface Temperature (°C) from the above features, benchmarked against XGBoost.

**4. Explainability** — SHAP (SHapley Additive exPlanations) values reveal which features drive each individual prediction, not just the model on average.

**5. Deployment** — final per-cell predictions exported to lightweight JSON, rendered as an interactive Leaflet.js map with a click-to-diagnose panel — no backend server required, fully static.

## Tech stack

- **Data & modeling:** Python, Google Earth Engine, `osmnx`, `geopandas`, `scikit-learn`, `xgboost`, `shap`
- **Frontend:** Leaflet.js, vanilla JavaScript, HTML/CSS
- **Hosting:** GitHub Pages (static, no backend)

## Project structure

```
heat-island-mapper/
├── 11_road_density.py          # Pull OSM road network per city
├── 12_road_density_per_cell.py # Compute road density per grid cell
├── 17_add_features.py          # Build final dataset (LST, NDVI, NDBI, Elevation)
├── 19_train_model_v2.py        # Train & evaluate the Random Forest / XGBoost models
├── 20_shap_v2.py                # Generate SHAP explainability plots
├── 22_add_coast_distance.py    # Add distance-to-coast feature (Karachi)
├── 23_export_for_web.py        # Export final datasets to JSON for the website
├── index.html                   # Interactive map (the live deliverable)
├── lahore_data.json             # Final Lahore dataset (web-ready)
├── karachi_data.json            # Final Karachi dataset (web-ready)
└── *.csv                        # Intermediate & final tabular datasets
```

## Running it locally

```bash
# clone the repo
git clone https://github.com/EmanKhaliq49/heat-island-mapper.git
cd heat-island-mapper

# serve the website locally (needed because browsers block local JSON fetches otherwise)
python -m http.server 8000
```

Then open `http://localhost:8000` in your browser.

*(To regenerate the data pipeline from scratch, you'll need a free [Google Earth Engine](https://earthengine.google.com/) account — see the numbered Python scripts for the full pipeline, run in order.)*

## Possible next steps

- Add a third city for a broader comparison
- Incorporate building height data for a more direct "shadow/shade" feature
- Add a temporal dimension — how do these patterns shift across seasons?
- A "what-if" simulator: predicted temperature change if vegetation cover increased by X%

## License

MIT
