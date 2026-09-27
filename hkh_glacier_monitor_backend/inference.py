import ee
import cv2
import numpy as np
import ee
import numpy as np
import rasterio
import io
import requests

from connecting_dagshub import load_from_cache, save_to_cache

def get_consistent_4d_image(aoi, target_year: int):
    """
    Guarantees perfectly matched 30m grid and 6-band spectrum structure
    exactly matching the Microsoft/ICIMOD training distribution.
    """
    # 1. Dynamically pick the right Landsat generation based on the timeline year requested
    if target_year <= 2012:
        # Use Landsat 7 (Matches exact training baseline)
        collection = "LANDSAT/LE07/C02/T1_L2" # my training sensor
        bands = ["SR_B1", "SR_B2", "SR_B3", "SR_B4", "SR_B5", "SR_B7"] # L7 mappings

    else:

        collection = "NASA/LE07/C02/T1_L2" # # or HLSS30 — already merges L8/9 + Sentinel-2
        bands = ["SR_B2", "SR_B3", "SR_B4", "SR_B5", "SR_B6", "SR_B7"] # L9 mappings

    # 2. Extract the clearest summer composite to avoid seasonal winter snow falses
    raw_sat = (
        ee.ImageCollection(collection)
        .filterBounds(aoi)
        .filterDate(f"{target_year}-06-01", f"{target_year}-09-30")
        .sort("CLOUD_COVER")
        .first()
    )
    
    # Read it out and standardize the band name aliases for your model wrapper
    optical_image = raw_sat.select(bands, ["Blue", "Green", "Red", "NIR", "SWIR1", "SWIR2"])
    optical_image = optical_image.multiply(0.0000275).add(-0.2)
    
    #  Fetch the SRTM Elevation baseline (Matches Microsoft dataset specification)
    # Re-project explicitly to match Landsat's grid positioning perfectly
    srtm = ee.Image("USGS/SRTMGL1_003").reproject(
        crs = optical_image.select("Blue").projection(), 
        scale = 30
    )
    
    # Glue them together into your virtual 7-band block
    return optical_image.addBands(srtm.select(["elevation"], ["DEM"])).clip(aoi)


def fetch_as_numpy(image : ee.image, aoi, size = 512) -> np.ndarray:

    """download the ee.image as geotiff bytes, reads into numpy
    return shapee (7, h, w) float32"""

    # generates the download url api
    url = image.getDownloadURL({
        "region" : aoi,
        "dimensions" : f"{size}x{size}", # i need 512*512 dimensions 
        "format" : "GEO_TIFF",
    })


    response = requests.get(url) # https get request to download the image bytes 
    response.raise_for_status()



    # rasterio read the bytes stream out ofthe memory
    with rasterio.open(io.BytesIO(response.content)) as src:
        array = src.read().astype(np.float32)  # (7, W, H)
    return array



def generate_texture_overlay(prediction_mask):
    """
    Converts a binary numpy prediction mask into an RGBA image matrix.
    Glacier predictions turn into an semi-transparent blue hue, empty spaces are invisible.
    """


    h, w = prediction_mask.shape
    rgba_image = np.zeros((h, w, 4), dtype=np.uint8)
    
    # Where    dataset model detects glacier presence:
    rgba_image[prediction_mask == 1] = [0, 191, 255, 180]  # DeepSkyBlue with 180 alpha transparency
    rgba_image[prediction_mask == 0] = [0, 0, 0, 0]        # Completely hidden transparent void
    
    # Compress into byte array to pass over API
    _, buffer = cv2.imencode('.png', rgba_image)
    return buffer.tobytes()



def get_glacier_array(glacier_name : str , year : int , optical_image, aoi ) -> np.ndarray:

    local_path = f"data/{glacier_name}/{year}/optical.tif"

    if load_from_cache(glacier_name, year, local_path):

        with rasterio.open(local_path) as src:

            readed = src.read().astype(np.float32)
            return readed


    raw_array = fetch_as_numpy(optical_image, aoi, local_path)
    save_to_cache(local_path, glacier_name, year)


    return raw_array
