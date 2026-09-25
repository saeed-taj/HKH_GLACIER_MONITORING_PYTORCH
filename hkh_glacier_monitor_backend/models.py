

from sqlalchemy import Integer, String, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone
from database import Base



class Authentication(Base):
    __tablename__="users"


    id : Mapped[str] = mapped_column(String, primary_key=True, index=True)
    username : Mapped[str] = mapped_column(String,  index=True)
    password: Mapped[str] = mapped_column(String, index=True)
    registed_at : Mapped[datetime] = mapped_column(DateTime, default=lambda : datetime.now(timezone.utc))
    login_at : Mapped[datetime] = mapped_column(DateTime, default=lambda : datetime.now(timezone.utc))


class Glacier(Base):
        
    __tablename__ = "glacier"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True)
    min_lat: Mapped[float] = mapped_column(Float)
    max_lat: Mapped[float] = mapped_column(Float)
    min_lon: Mapped[float] = mapped_column(Float)
    max_lon: Mapped[float] = mapped_column(Float)
    dem_path: Mapped[str] = mapped_column(String)



class GlacierRecord(Base):

    __tablename__ = "glacier_record"

    __table_args__ = (UniqueConstraint("glacier_id", "year", "model_version"),)


    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    glacier_id: Mapped[int] = mapped_column(ForeignKey("glacier.id"))
    glacier_name: Mapped[str] = mapped_column(String, index=True)
    year: Mapped[int] = mapped_column(Integer)
    area_sq_km: Mapped[float] = mapped_column(Float)
    captured_at: Mapped[datetime] = mapped_column(DateTime, default=lambda : datetime.now(timezone.utc))    
    mask_path: Mapped[str] = mapped_column(String)
    
