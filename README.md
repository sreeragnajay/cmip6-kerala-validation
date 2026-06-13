# CMIP6 Historical GCM Validation & Bias-Correction Analysis Pipeline: Kerala Watersheds

An automated, cloud-optimized, and localized pipeline designed to ingest, process, and evaluate both raw and bias-corrected CMIP6 Global Climate Model (GCM) historical precipitation datasets against observation networks over Kerala, India.

## 📁 Repository Framework

- `/gee_scripts`: JavaScript modules deployed on Google Earth Engine (GEE) using server-side C++ array operations (`getRegion`) for ultra-fast raw GCM data extraction.
- `/scripts`: Python processing automation routines utilizing `scipy.spatial.cKDTree` for 1-to-1 coordinate snapping, temporal alignment, duplicate record sanitization, and downscaling matrix reshapes.

---

## 📊 Datasets Evaluated

The pipeline structurally compares and validates two separate variants of the CMIP6 historical precipitation framework against a common observation baseline:

1. **Observed Baseline (IMD):** High-resolution daily gridded rainfall data provided by the **Indian Meteorological Department (IMD)**, scaled down-column for 77 localized watershed tracking nodes.
2. **Raw GCMs (NASA NEX-GDDP-CMIP6):** Raw daily precipitation flux outputs fetched directly via the cloud at a spatial resolution of $0.25^\circ \times 0.25^\circ$.
3. **Bias-Corrected GCMs (IIT Gandhinagar / Zenodo):** Daily downscaled, bias-corrected projections ($0.25^\circ$ resolution) optimized for Indian sub-continental river basins (specifically extracted from the *West Coast* regional hydrologic domain using empirical quantile mapping).

---

## 🚀 Pipeline Workflow

### Phase 1: Data Ingestion & Extraction
* **Raw GCM Track:** Server-side loop routing extracts the raw daily precipitation flux (`pr` band in $kg/m^2/s$) for 13 distinct models. It queries the target coordinate arrays from **January 1, 1990, to December 31, 2014**. Unit transformation to $mm/day$ ($86,400 \times pr$) is executed on the fly prior to drive compilation.
* **Bias-Corrected GCM Track:** Local binary archives extracted from the hydrologic database are read. Columns are mapped by long-term tracking grids corresponding to regional gauge networks across the study domain.

### Phase 2: Local Reshaping, Snapping, & Sanitization
Both dataset tracks are systematically standardized into matching wide-matrix rain-gauge data structures via Python (`pandas`, `scipy`):
1. **Spatial Coordinate Snapping:** Coordinates are explicitly anchored to the primary tracking grid using a multi-dimensional nearest neighbor search tree (`cKDTree`).
2. **Data Deduplication:** Structural record overlaps or temporal image tracking duplicate splits inside GCM database tables are purged using strict subset filtering (`.drop_duplicates(subset=['date', 'latitude', 'longitude'])`).
3. **Matrix Pivot:** Long tables are converted into clear database tables (Dates as rows, Grid Stations 1–77 as structured columns).
4. **Temporal Resampling:** Daily values are accumulated into standard month-start totals (`.resample('MS').sum()`) and formatted to strings matching a clean `YYYY-MM` schema.

### Phase 3: Dual-Track Statistical Validation
To assess model accuracy before and after bias mitigation, independent validation modules calculate performance benchmarks for all 13 models against the identical IMD target matrix over the shared historical time window (**1990-01 to 2014-11**). 

Separate statistics sheets are generated down-column for each model across all 77 stations tracking three core engineering metrics:
* **Pearson's Correlation Coefficient ($r$):** Captures temporal alignment and monsoon seasonality rhythms.
* **Root Mean Squared Error (RMSE):** Captures variance intensity, mathematically standardized back to an intuitive daily scaling rate ($mm/day$).
* **Percent Bias (PBIAS %):** Quantifies systematic volume over- or under-estimation errors.

---

## 🛠️ Performance Metrics Explanations

### Pearson's Correlation Coefficient ($r$)
Measures the linear phase matching between model variations and actual field observations:
$$r = \frac{\sum (GCM_i - \overline{GCM})(IMD_i - \overline{IMD})}{\sqrt{\sum (GCM_i - \overline{GCM})^2 \sum (IMD_i - \overline{IMD})^2}}$$

### Root Mean Squared Error (RMSE)
Measures average error magnitude. It is evaluated at the monthly scale and divided by the mean month duration ($30.4375$) to evaluate errors relative to daily scale flows:
$$RMSE_{monthly} = \sqrt{\frac{1}{n}\sum_{i=1}^{n} (GCM_i - IMD_i)^2}$$
$$RMSE_{daily} = \frac{RMSE_{monthly}}{30.4375}$$

### Percent Bias (PBIAS)
Evaluates the continuous direction and scale of systematic mass balance over- or under-estimation errors:
$$PBIAS = 100 \times \left[ \frac{\sum_{i=1}^{n} (GCM_i - IMD_i)}{\sum_{i=1}^{n} IMD_i} \right]$$

---

## 📈 Supported CMIP6 GCM Framework
The pipeline successfully resolves, formats, and validates the following 13 models across both raw and bias-corrected iterations:
1. `ACCESS-CM2`
2. `ACCESS-ESM1-5`
3. `BCC-CSM2-MR`
4. `CanESM5`
5. `EC-Earth3`
6. `EC-Earth3-Veg-LR`
7. `INM-CM4-8`
8. `INM-CM5-0`
9. `MPI-ESM1-2-HR`
10. `MPI-ESM1-2-LR`
11. `MRI-ESM2-0`
12. `NorESM2-LM`
13. `NorESM2-MM`
