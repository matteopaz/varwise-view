
port=9000
preload=False
sideloader_threads=8

query_radius=5 # NEOWISE Single-Exposure Catalog search radius in arcseconds

USE_PURE_CATALOG=True # Use the pure version of VarWISE or Complete (False)
QUERY="type LIKE 'ea' AND period_significance > 1.5" # SQL query Constraints for VarWISE
SORTBY=("period_significance", False) # Sort by column and ascending (True) or descending (False)
# Example: QUERY="W1mag < 15 AND variability_snr > 5.0 AND type LIKE 'agn' "
ROWLIMIT=20 # Maximum number of objects retrieved within QUERY constraints