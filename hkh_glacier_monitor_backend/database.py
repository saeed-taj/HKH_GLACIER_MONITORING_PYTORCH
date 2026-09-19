import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase



load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(DATABASE_URL, echo=True)


AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

















"""
glacier = Glacier(name="Baltoro")
session.add(glacier)
session.commit()  # Row 1 exists with the name



# 1. Look up the row you already made (e.g., by its unique name)
existing_glacier = (
    session.query(Glacier).filter(Glacier.name == "Baltoro").first()
)

# 2. Update the max_lon on that exact row
if existing_glacier:
    existing_glacier.max_lon = 76.5
    session.commit()  # Updates Row 1

"""