# Installation

Required packages:
```
pip install astroquery astropy
pip install plotly joblib pandas numpy pandasql
pip install flask
```

Clone this repository:

```git clone https://github.com/matteopaz/varwise-view.git```

# Usage

Name your catalog/subcatalog of choice `catalog.csv` and place into the root directory. Alternatively, in `__init__.py`, define the `QUERY` SQL constraint and run `python filter.py`, which will produce a subset of either VarWISE or VarWISE pure.

To start the server, run `python app.py`. Navigate to `localhost:5000` on your browser. Light mode is strongly recommended.
