import geopandas as gpd # type: ignore
import numpy as np # type: ignore
from sklearn.cluster import HDBSCAN # type: ignore

def cluster_thermal_detections(detections_gdf: gpd.GeoDataFrame) -> np.ndarray:
    """
    Groups raw detections into persistent thermal entities.
    detections_gdf: GeoDataFrame containing point geometries in EPSG:4326.
    """
    if len(detections_gdf) < 3:
        # Not enough points to cluster effectively
        return np.full(len(detections_gdf), -1)

    # Project to a metric CRS (e.g., Web Mercator) for distance calculations in meters
    projected_gdf = detections_gdf.to_crs(epsg=3857)
    coords = np.column_stack((projected_gdf.geometry.x, projected_gdf.geometry.y))
    
    # HDBSCAN for density-based clustering. 
    # cluster_selection_epsilon ensures points within ~500m are grouped.
    clusterer = HDBSCAN(min_cluster_size=3, cluster_selection_epsilon=500.0)
    labels = clusterer.fit_predict(coords)
    
    return labels
