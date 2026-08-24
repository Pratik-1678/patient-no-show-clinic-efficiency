# Patient No-Show & Clinic Efficiency Analysis

End-to-end analytics project on the Kaggle Medical Appointment No Shows dataset — Excel audit, Python
cleaning/EDA/statistical validation, MySQL business queries, Power BI dashboard, and an interactive Streamlit app.

*(Full README with findings, screenshots, and setup instructions coming in the next step.)*

## Structure
- `data/` — raw and cleaned datasets
- `notebooks/` — 5 Jupyter notebooks (cleaning → EDA → statistical validation → segmentation → efficiency)
- `sql/` — MySQL schema + business queries
- `powerbi/` — data model CSVs + your `.pbix` file
- `streamlit/` — interactive dashboard (`app.py`)
- `docs/` — data dictionary, business insights, executive summary, Power BI documentation
- `excel/` — initial data audit workbook
- `outputs/` — charts and dashboard screenshots

## How to Run
```bash
pip install -r requirements.txt
jupyter notebook notebooks/01_data_cleaning.ipynb   # run notebooks 01-05 in order
streamlit run streamlit/app.py                       # from inside streamlit/, or adjust the data path
```
