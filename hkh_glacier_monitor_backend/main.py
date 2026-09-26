from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_db
from models import GlacierRecord
from fastapi.middleware.cors import CORSMiddleware
from routes import users
from dotenv import load_dotenv


app = FastAPI(title="HKH Glacier Monitor Backend")

load_dotenv()   

app.include_router(users.router, prefix="/users", tags=["user section"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]

)

@app.post("/glacier/name")
async def glacier_new(name : str , db : AsyncSession = Depends(get_db)):
    try: 
        new_glacier_record = GlacierRecord(glacier_name=name)

        db.add(new_glacier_record)

        await db.commit()
        await db.refresh(new_glacier_record)

        return {"message": "record saved ", "data ": new_glacier_record.id }
    except Exception as e:

        await db.rollback()

        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/glacier/size")
async def glacier_size(size: float, db : AsyncSession = Depends(get_db)):
    try:

        new_size = GlacierRecord(area_sq_km=size)

        db.add(new_size)

        await db.commit()
        await db.refresh(new_size)


        return {"message saved " }

    except Exception as e:
        await db.rollback()

        raise HTTPException(status_code=500, detail=f"database error : {str(e)}")


@app.get("/glacier/list")
async def glacier_list(db : AsyncSession = Depends(get_db)):

    query = select(GlacierRecord.glacier_name)

    result = await db.execute(query)

    names = result.all()

    return names













































