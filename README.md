# Installation

Clone this repository:

```git clone https://github.com/matteopaz/varwise-view.git```

Install the required packages:
```
pip install astroquery astropy
pip install plotly joblib pandas numpy pandasql
pip install flask
```

# Setup
First, you will need the VarWISE and VarWISE pure catalogs. Place those `csv` files into the `/varwise_cats/` directory as titled `VarWISE` and `pure_VarWISE`.

In `__init__.py`, define the `QUERY` SQL constraint and run `python filter.py`, which will produce a subset of either VarWISE or VarWISE pure, saving it to `catalog.csv`. You may also place your own subcatalog in place of this generated file.


# Running
To start the server, run `python app.py`. Navigate to `localhost:5000` on your browser. Light mode is strongly recommended.
