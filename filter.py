import pandas as pd
from pandasql import sqldf
from __init__ import QUERY, ROWLIMIT, USE_PURE_CATALOG, SORTBY

catalog = pd.read_csv("varwise_cats/pure_VarWISE.csv" if USE_PURE_CATALOG else "varwise_cats/VarWISE.csv")
catalog = catalog.sort_values(by=SORTBY[0], ascending=SORTBY[1])

result = sqldf(f"SELECT * FROM catalog WHERE {QUERY}", globals()).head(ROWLIMIT).set_index("cluster_id")

result.to_csv("catalog.csv")