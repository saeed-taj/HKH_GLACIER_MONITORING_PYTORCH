import io
import ee
import numpy as np
import torch
from fastapi import FastAPI, Request, APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from models import Glacier
from database import AsyncSessionLocal, Base, engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from inference import get_consistent_4d_image, generate_texture_overlay, get_glacier_array
import json


try:
    ee.Initialize()

except Exception:
    pass


router = APIRouter()


with open("norm_stats.json") as f:
    stats = json.load(f)

opt_mean = np.array(stats["optical_mean"]).reshape(6,1,1)   # (6,1,1)row, col, depth
opt_std = np.array(stats["optical_std"]).reshape(6,1,1)
dem_mean = np.float32(stats["dem_mean"][0])
dem_std = np.float32(stats["dem_std"][0])


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

async def get_db(): # Context-Managed Dependency 
    async with AsyncSessionLocal() as session:
        try:
            yield session

        finally:
            await session.close()



class GlacierRequest(BaseModel):
    name: str
    year: int


class bounding_box(BaseModel):
    min_lat: float
    max_lat: float
    min_lon: float
    max_lon: float
    year: int
    glacier_name : str


async def intercept_glacier(payload : GlacierRequest , db : AsyncSession = Depends(get_db)) -> bounding_box:


    all_coords = select(Glacier.min_lat, Glacier.max_lat, Glacier.max_lon, Glacier.min_lon).where(Glacier.name == payload.name)

    result = await db.execute(all_coords)
    coords = result.first()

    if not coords:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Glacier '{payload.name}' not found in db"
        )

    if coords:
        min_lat , max_lat, min_lon, max_lon = coords 
        print(f"min_lat : {min_lat} , max_lat : {max_lat} , min_lon : {min_lon} , max_lon :  {max_lon} ")

    else: 
       print("not record found!!!")


    return bounding_box(
        min_lat = coords.min_lat,
        max_lat = coords.max_lat,
        min_lon = coords.min_lon,
        max_lon = coords.max_lon,
        year = payload.year,
        glacier_name = payload.name
    )
    


@router.post("/glacier")
async def galcier_name(final_glacier : bounding_box = Depends(intercept_glacier )):

    # area of interest 
    aoi = ee.Geometry.BBox(final_glacier.min_lon, final_glacier.min_lat, final_glacier.max_lon, final_glacier.max_lat)
 

    optical_image = get_consistent_4d_image(aoi, final_glacier.year)


    raw_array = get_glacier_array(glacier_name = final_glacier.glacier_name,year = final_glacier.year,
                                  optical_image = optical_image,
                                   aoi = aoi)

    optical_norm = (raw_array[:6] - opt_mean) / opt_std
    dem_norm = (raw_array[ 6 : 7 ] - dem_mean ) / dem_std

    normalized = np.concatenate([optical_norm, dem_norm], axis=0)

    tensor = torch.from_numpy(normalized).float().unsqueeze(0).to(device)


    model.eval()
    with torch.no_grad():
        logits = model(tensor)
        probs = torch.sigmoid(logits)
        prediction_mask = (probs > 0.5).squeeze().cpu().numpy().astype(np.uint8)

    # here i will use the prithvi model and use for the inference 

    # here when model will ready i will put the


    # Pseudo-flow inside your FastAPI router:
    # 1. Fetch 7-band numpy array via ee.data.computePixels
     # 2. pass array into PyTorch Model -> outputs segmentation_mask (H x W)



    prediction_mask_result = generate_texture_overlay(prediction_mask)

    # this is ready to send back to show on the frontend i guess for now 


    return prediction_mask_result
