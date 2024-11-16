import numpy as np
import pandas as pd
import plotly.graph_objects as go
from joblib import Parallel, delayed
from flask import Flask, render_template
from __init__ import query_ahead, port
from main import Loader, Object, plot_lightcurve
from json import dumps
from plotly import utils
import os
import pickle as pkl

catalog = pd.read_csv("catalog.csv").set_index("cluster_id")
cids = list(catalog.index)
app = Flask(__name__)

def cache(cid):
    cached_cids = [f[:-4] for f in os.listdir("cache") if f.endswith(".pkl")]
    if str(cid) in cached_cids:
        with open(f"cache/{cid}.pkl", "rb") as f:
            return pkl.load(f)
    else:
        obj = Object(catalog.loc[cid])
        with open(f"cache/{cid}.pkl", "wb") as f:
            pkl.dump(obj, f)
        return obj
    

@app.route("/")
def idx():
    # convert catalog to list of dicts
    tbl = catalog.reset_index()
    data = tbl.to_dict(orient="records")
    data_json = dumps(data)
    cols = list(tbl.columns)
    cols_json = dumps(cols)
    return render_template("index.html", data=data_json, cols=cols_json)

@app.route('/<cid>')
def daily_post(cid):
    cid = int(cid)
    if cid not in catalog.index:
        return "Not found", 404
    
    obj = cache(cid)
    
    fig = plot_lightcurve(obj)
    lightcurve = dumps(fig, cls=utils.PlotlyJSONEncoder)
    pdfig = plot_lightcurve(obj, period=1e6, periodic=True)
    pdlightcurve = dumps(pdfig, cls=utils.PlotlyJSONEncoder)
    title = obj.name
    
    idx = cids.index(cid)
    previd = cids[idx - 1] if idx > 0 else ""
    nextid = cids[idx + 1] if idx < len(cids) - 1 else ""
    
    catalogstats = {c: obj.row[c] for c in obj.row.index}
    return render_template("object.html", titletext=title, lc_json=lightcurve, folded_lc_json=pdlightcurve, **catalogstats, previd=previd, nextid=nextid)
    
if __name__ == "__main__":
    app.run(port=port, debug=True)