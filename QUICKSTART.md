# 🚀 QUICK START GUIDE

## Prerequisites
- Python 3.10 or higher
- 8GB RAM minimum
- Git (for version control)

## Setup (5 minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Verify Data
Ensure datasets are in `data/raw/`:
- api_data_aadhar_enrolment/ (3 CSV files)
- api_data_aadhar_biometric/ (4 CSV files)  
- api_data_aadhar_demographic/ (5 CSV files)

## Execution (30-45 minutes)

### Run All Analyses
```bash
# Execute in order
for i in {01..13}; do
    python src/${i}_*.py
done
```

### Or Run Individually

**Phase 1: Data Prep (5 min)**
```bash
python src/01_data_cleaning.py
python src/02_exploratory_analysis.py
```

**Phase 2: Analysis (10 min)**
```bash
python src/03_state_trend_analysis.py
python src/04_child_gap_analysis.py
python src/05_biometric_compliance.py
python src/06_anomaly_detection.py
python src/07_anomaly_visualizations.py
```

**Phase 3: Predictions (15 min)**
```bash
python src/08_forecasting_models.py
python src/09_forecast_visualizations.py
python src/10_ml_models.py
python src/11_ml_visualizations.py
```

**Phase 4: Final Output (5 min)**
```bash
python src/12_final_dashboards.py
python src/13_generate_report.py
```

## Outputs

### Results (`results/`)
- CSV files with analysis outputs
- Trained models (.pkl files)
- Comprehensive insights report

### Visualizations (`visualizations/`)
- 7 categories of charts
- 40+ professional visualizations
- Ready for presentation

## Troubleshooting

**Issue**: Missing data files
**Solution**: Check `data/raw/` directory structure

**Issue**: Memory error
**Solution**: Process data in chunks (scripts auto-handle this)

**Issue**: Package conflicts
**Solution**: Use virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

## Next Steps

1. Review `results/STEP13_comprehensive_insights_report.txt`
2. Explore visualizations in `visualizations/`
3. Customize analysis parameters in scripts
4. Generate custom dashboards

## Support

- Check `docs/METHODOLOGY.md` for technical details
- Review `docs/VISUALIZATION_GUIDE.md` for chart explanations
- See individual script docstrings for parameter options
