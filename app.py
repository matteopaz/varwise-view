import numpy as np
import pandas as pd
import plotly.graph_objects as go
from joblib import Parallel, delayed
from flask import Flask, render_template, send_from_directory
from __init__ import preload, port, sideloader_threads
from main import Loader, Object, plot_lightcurve
from json import dumps
from plotly import utils
import os
import pickle as pkl
import concurrent.futures

catalog = pd.read_csv("catalog.csv").set_index("cluster_id")
cids = list(catalog.index)
app = Flask(__name__)

def cache(cid):
    print(f"Caching {cid}")
    cached_cids = [f[:-4] for f in os.listdir("cache") if f.endswith(".pkl")]
    if str(cid) in cached_cids:
        with open(f"cache/{cid}.pkl", "rb") as f:
            return pkl.load(f)
    else:
        obj = Object(catalog.loc[cid])
        with open(f"cache/{cid}.pkl", "wb") as f:
            pkl.dump(obj, f)
        return obj

def cache_all(cids):
    for cid in cids:
        cache(cid)

if preload:
    Parallel(n_jobs=sideloader_threads)(delayed(cache)(cid) for cid in cids)


@app.route("/")
def idx():
    # convert catalog to list of dicts
    tbl = catalog.reset_index()
    tbl["cluster_id"] = tbl["cluster_id"].astype(str)
    data = tbl.to_dict(orient="records")
    data_json = dumps(data)
    cols = list(tbl.columns)
    cols_json = dumps(cols)
    return render_template("index.html", data=data_json, cols=cols_json)

@app.route('/object/<cid>')
def getobject(cid):
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
    previd = str(cids[(idx - 1) % len(cids)])
    nextid = str(cids[(idx + 1) % len(cids)])
    prevnext = (previd, nextid)

    # start a non-blocking task to cache the next object
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_previd = executor.submit(cache, previd)
        future_nextid = executor.submit(cache, nextid)
    
    catalogstats = {c: obj.row[c] for c in obj.row.index}
    dfpd = catalogstats["period_peak_1"]
    if not (dfpd > 0): # if period is not available, set default period to 4000 days
        dfpd = 4000.0

    lc_table = pd.DataFrame({"mjd": obj.timeseries["t"], "w1mpro": obj.timeseries["w1"], "w1sigmpro": obj.timeseries["w1s"], 
                        "w2mpro": obj.timeseries["w2"], "w2sigmpro": obj.timeseries["w2s"]})
    csv = lc_table.to_csv(index=False)
    return render_template("object.html", titletext=title, lc_json=lightcurve, folded_lc_json=pdlightcurve, **catalogstats, prevnext=dumps(prevnext), defaultperiod=dfpd, lc_csv=dumps(csv))
    
# @app.route('/download_lc/<cid>')
# def download_lc(cid):
#     cid = int(cid)
#     if cid not in catalog.index:
#         return "Not found", 404
    
#     obj = cache(cid)
#     tbl = pd.DataFrame({"mjd": obj.timeseries["t"], "w1mpro": obj.timeseries["w1"], "w1sigmpro": obj.timeseries["w1s"], 
#                         "w2": obj.timeseries["w2"], "w2sigmpro": obj.timeseries["w2s"]})
    
#     return tbl.to_csv(index=False)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


with concurrent.futures.ThreadPoolExecutor() as executor:

    # launch up to sideloader_threads sideloader processes
    for i in range(sideloader_threads):
        executor.submit(cache_all, cids[i::sideloader_threads])
    print("Sideloader processes ({}) launched.".format(sideloader_threads))
    
    if __name__ == "__main__":
        app.run(port=port, debug=True)
    print("Sideloader processes launched.")