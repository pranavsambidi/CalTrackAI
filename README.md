# CalTrackAI

The primary objective of this project is to build an AI-powered system that can estimate the calorie and nutritional content of meals directly from food images. The system aims to reduce the burden of manual calorie logging and provide accurate nutritional breakdowns to support health monitoring and personalized diet planning.


```
CalTrackAI/
├── data/
│   ├── raw/                                 # Original data sources (unmodified)
│   │   ├── food-101/                        # Food-101 dataset (images + metadata)
│   │   │   ├── images/                      # Raw image folders (e.g., apple_pie/, pizza/, salad/, etc.)
│   │   │   └── meta/                        # JSON metadata files (train/test splits)
│   │   │       ├── train.json
│   │   │       └── test.json
│   │   └── usda_food_data.csv               # Nutrition dataset from USDA FoodData Central
│   │
│   ├── clean/                               # Cleaned & processed datasets
│   │   ├── train_cleaned.csv                # Merged Food-101 + USDA dataset (training)
│   │   └── test_cleaned.csv                 # Merged Food-101 + USDA dataset (testing)
│
├── notebooks/                               # Jupyter notebooks for development & analysis
│   ├── data_preparation.ipynb               # Handles data integration, cleaning, and preprocessing
│   └── risk_trustworthiness.ipynb           # Implements fairness, privacy, and drift detection strategies
│
├── .gitignore                               # Specifies files/folders to exclude from GitHub (e.g., large image data)
├── README.md                                # Project overview and documentation
└── requirements.txt                         # Python dependencies (TensorFlow, Fairlearn, Diffprivlib, SHAP, etc.)
```

---

### Folder Summary

* **`data/raw/`** → Contains all raw input datasets (Food-101 images and USDA FoodData CSV).
* **`data/clean/`** → Contains cleaned, merged, and processed CSV files ready for training.
* **`notebooks/`** → Includes modular notebooks for each phase of the project:

  * `data_preparation.ipynb` → Cleans and preprocesses datasets.
  * `risk_trustworthiness.ipynb` → Evaluates fairness, privacy, and risk metrics.
* **`.gitignore`** → Ensures large datasets and unnecessary files are excluded from GitHub.
* **`requirements.txt`** → Lists dependencies to recreate the environment quickly.

---
