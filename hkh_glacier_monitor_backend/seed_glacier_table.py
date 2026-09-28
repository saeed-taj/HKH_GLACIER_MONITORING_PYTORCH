
from database import AsyncSessionLocal, Base, engine
from models import Glacier

GLACIER_SEED_DATA = [
    {
        "name": "Siachen Glacier",
        "min_lat": 35.15, "max_lat": 35.65,
        "min_lon": 76.75, "max_lon": 77.25,
        "dem_path": "/dems/siachen.tif"
    },
    {
        "name": "Baltoro Glacier",
        "min_lat": 35.65, "max_lat": 35.95,
        "min_lon": 76.10, "max_lon": 76.70,
        "dem_path": "/dems/baltoro.tif"
    },
    {
        "name": "Biafo Glacier",
        "min_lat": 35.80, "max_lat": 36.15,
        "min_lon": 75.60, "max_lon": 76.10,
        "dem_path": "/dems/biafo.tif"
    },
    {
        "name": "Hispar Glacier",
        "min_lat": 36.00, "max_lat": 36.20,
        "min_lon": 74.95, "max_lon": 75.60,
        "dem_path": "/dems/hispar.tif"
    },
    {
        "name": "Batura Glacier",
        "min_lat": 36.45, "max_lat": 36.60,
        "min_lon": 74.15, "max_lon": 74.85,
        "dem_path": "/dems/batura.tif"
    },
    {
        "name": "Khumbu Glacier (Everest Region)",
        "min_lat": 27.90, "max_lat": 28.02,
        "min_lon": 86.82, "max_lon": 86.95,
        "dem_path": "/dems/khumbu.tif"
    },
    {
        "name": "Gangotri Glacier",
        "min_lat": 30.80, "max_lat": 31.05,
        "min_lon": 79.15, "max_lon": 79.35,
        "dem_path": "/dems/gangotri.tif"
    }
]


def seed_glacier():

    db = AsyncSessionLocal()

    try:

        for i in GLACIER_SEED_DATA:
            exists = db.query(Glacier).filter(Glacier.name == i["name"]).first()

            if not exists:
                glacier = Glacier(
                    name = i["name"],
                    min_lat = i["min_lat"],
                    max_lat = i["max_lat"],
                    min_lon = i["min_lon"],
                    max_lon = i["max_lon"],
                    dem_path = i["dem_path"] 
                )

                db.add(glacier)
                db.commit()
                print("added to db  ")


    except Exception as e:

        db.rollback()
        print(f"not stored in db {e}")


    finally:
        db.close()



if __name__ == "__main__":

    seed_glacier()

