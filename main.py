import numpy as np
import pandas as pd
import astropy.units as u
import astropy.coordinates as ac
import astroquery as aq
from astroquery.ipac.irsa import Irsa
from __init__ import query_radius
from multiprocessing import Process
from plotly import graph_objects as go

Irsa.ROW_LIMIT = 50000

class Object:
    def __init__(self, catalog_row):
        self.row = catalog_row
        self.ra = self.row['RAJ2000']
        self.dec = self.row['DecJ2000']
        self.coord = ac.SkyCoord(ra=self.ra*u.deg, dec=self.dec*u.deg, frame='icrs')
        self.name = self.row['Designation'] 
        self.type = self.row['type']
        self.period = self.row['period_peak_1']
        if not isinstance(self.period, float):
            self.period = False
        self.timeseries = self.query_neowise()
        
    def query_neowise(self):
        res = Irsa.query_region(self.coord, catalog='neowiser_p1bs_psd', radius=query_radius*u.arcsec,
                                spatial='Cone', columns='w1mpro,w1sigmpro,w2mpro,w2sigmpro,mjd,cc_flags,qual_frame,w1rchi2')
        tbl = res.to_pandas()
        
        tbl = tbl[tbl["w1rchi2"] < 10]
        tbl = tbl[tbl["qual_frame"] > 0]
        tbl = tbl[tbl["w1sigmpro"] > 0]
        tbl = tbl[tbl["cc_flags"] == "0000"]
        
        w1 = np.array(tbl["w1mpro"].values)
        w1s = np.array(tbl["w1sigmpro"].values)
        w2 = np.array(tbl["w2mpro"].values)
        w2s = np.array(tbl["w2sigmpro"].values)
        t = np.array(tbl["mjd"].values)
        
        return {"w1": w1, "w1s": w1s, "w2": w2, "w2s": w2s, "t": t}
    
class Loader:
    def __init__(self, catalog: pd.DataFrame, query_ahead=10):
        self.catalog = catalog
        self.buffer = []
        self.query_ahead = query_ahead
        self.ROW = 0
        
    def nextrow(self):
        row = self.catalog.iloc[self.ROW]
        self.ROW += 1
        return row
        
    def build_buffer(self):
        if self.query_ahead == False:
            self.buffer.append(Object(self.nextrow()))
            return
        
        for _ in range(self.query_ahead - len(self.buffer)):
            print("Adding to buffer")
            self.buffer.append(Object(self.nextrow()))
    
    def __iter__(self):
        self.ROW = 0
        self.buffer.append(Object(self.nextrow()))
        self.build_buffer()
        return self
    
    def __len__(self):
        return len(self.catalog)
    
    def __next__(self):
        obj = self.buffer.pop(0)
        self.build_buffer()
        return obj
        
def plot_lightcurve(obj, periodic=False, period=0):
    fig = go.Figure()
    t = obj.timeseries["t"]
    if periodic and period > 0:
        t = t % period
    
    w1 = obj.timeseries["w1"]
    w1s = obj.timeseries["w1s"]
    w2 = obj.timeseries["w2"]
    w2s = obj.timeseries["w2s"]
    
    w12 = w1 - w2
    w12s = np.sqrt(w1s**2 + w2s**2)
    
    fig.add_trace(go.Scatter(x=t, y=w1, mode='markers', marker=dict(size=5, color="blue"), opacity=0.75, marker_symbol="square", error_y=dict(type='data', array=w1s, visible=True, color="rgba(0,0,255,0.35)"), name='W1'))
    if not periodic:
        fig.add_trace(go.Scatter(x=t, y=w2, mode='markers', marker=dict(size=5, color="red"), opacity=0.75, marker_symbol="square", error_y=dict(type='data', array=w2s, visible=True, color="rgba(255,0,0,0.35)"), name='W2'))
        fig.add_trace(go.Scatter(x=t, y=w12, mode='markers', marker=dict(size=5, color="green"), opacity=0.75, marker_symbol="diamond", error_y=dict(type='data', array=w12s, visible=True, color="rgba(0,255,0,0.35)"), name='W1-W2'))
        # only W1 should be visible at first
        fig.data[1].visible = "legendonly"
        fig.data[2].visible = "legendonly"
    
    fig.update_yaxes(autorange="reversed")
    name = "Full NEOWISE Lightcurve" if not periodic else "p = %.5fd" % period
    fig.update_layout(title=name, xaxis_title='Time (MJD)', yaxis_title='Magnitude') 
    return fig