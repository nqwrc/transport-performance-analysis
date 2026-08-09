# Transport Performance Analysis 🚚

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![pandas](https://img.shields.io/badge/pandas-2.0+-150458.svg?style=flat&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-F37626.svg?style=flat&logo=jupyter&logoColor=white)](https://jupyter.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

On-time delivery, cost-per-route analytics, and discrepancy identification for a **B2B/B2C furniture transport operation**. Features synthetic route-level data modeled on real-world delivery rounds (province zones, 2h vs 4h agreed time windows, driver handling times, and transport discrepancy patterns).

---

## 📈 Analysis Pipeline & Flow

```mermaid
flowchart LR
    A[Route Simulator\ndata/generate_data.py] -->|4,593 Deliveries / 769 Routes| B[Raw CSV Data\ndata/deliveries.csv]
    B -->|Pandas Ingestion| C[EDA & Aggregation Engine\nnotebooks/01_transport_analysis.ipynb]
    C -->|On-Time Window SLA| D[Zone & Window Insights]
    C -->|Cost Allocation| E[Cost-Per-Item & Cost-Per-Route KPIs]
```

---

## 🎯 Key Operational Findings

- **Punctuality Drift Across Stop Sequence**: On-time rate drops from **97% at Stop 1** to **75% by Stop 7** due to cumulative handling delay propagation.
- **B2B vs B2C Failure Modes**: B2B delivery windows (2h) experience severe lateness in far zones (61.0% in Ferrara vs 98.7% in depot city) due to 60+ km outbound legs.
- **Cost Normalization (Per Route vs Per Item)**: Consolidating far-zone deliveries reduces per-item cost despite higher route distance costs.

---

## 🚀 Quickstart

```bash
# 1. Clone repository
git clone https://github.com/nqwrc/transport-performance-analysis.git
cd transport-performance-analysis

# 2. Install requirements & generate reproducible data
pip install -r requirements.txt
python data/generate_data.py

# 3. Launch Jupyter Notebook analysis
jupyter notebook notebooks/01_transport_analysis.ipynb
```

---

## 📝 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for details.
