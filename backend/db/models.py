import datetime
from typing import List, Optional
from sqlalchemy import ForeignKey, String, Integer, Float, Boolean, Date, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class Train(Base):
    __tablename__ = "trains"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    train_number: Mapped[str] = mapped_column(String(10), unique=True, index=True)
    train_name: Mapped[str] = mapped_column(String(100))
    train_type: Mapped[str] = mapped_column(String(50))  # e.g., Rajdhani, Shatabdi, Express

    tickets: Mapped[List["Ticket"]] = relationship("Ticket", back_populates="train")

class Route(Base):
    __tablename__ = "routes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_station: Mapped[str] = mapped_column(String(10), index=True)
    dest_station: Mapped[str] = mapped_column(String(10), index=True)
    distance_km: Mapped[float] = mapped_column(Float)
    avg_confirm_rate: Mapped[float] = mapped_column(Float, default=0.75)

    tickets: Mapped[List["Ticket"]] = relationship("Ticket", back_populates="route")

class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    train_id: Mapped[int] = mapped_column(Integer, ForeignKey("trains.id"), index=True)
    route_id: Mapped[int] = mapped_column(Integer, ForeignKey("routes.id"), index=True)
    quota: Mapped[str] = mapped_column(String(5))  # GN, TQ, LD, SS
    coach_class: Mapped[str] = mapped_column(String(5))  # SL, 3A, 2A, 1A
    initial_wl: Mapped[int] = mapped_column(Integer)
    final_wl: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    journey_date: Mapped[datetime.date] = mapped_column(Date)
    booked_at: Mapped[datetime.datetime] = mapped_column(DateTime)

    train: Mapped["Train"] = relationship("Train", back_populates="tickets")
    route: Mapped["Route"] = relationship("Route", back_populates="tickets")
    snapshots: Mapped[List["WLSnapshot"]] = relationship("WLSnapshot", back_populates="ticket", cascade="all, delete-orphan")
    predictions: Mapped[List["Prediction"]] = relationship("Prediction", back_populates="ticket", cascade="all, delete-orphan")

class WLSnapshot(Base):
    __tablename__ = "wl_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ticket_id: Mapped[int] = mapped_column(Integer, ForeignKey("tickets.id", ondelete="CASCADE"), index=True)
    wl_number: Mapped[int] = mapped_column(Integer)
    hours_to_departure: Mapped[int] = mapped_column(Integer)  # 72, 48, 24, 12, 2
    recorded_at: Mapped[datetime.datetime] = mapped_column(DateTime)

    ticket: Mapped["Ticket"] = relationship("Ticket", back_populates="snapshots")

class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ticket_id: Mapped[int] = mapped_column(Integer, ForeignKey("tickets.id", ondelete="CASCADE"), index=True)
    probability: Mapped[float] = mapped_column(Float)
    model_version: Mapped[str] = mapped_column(String(50))
    predicted_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

    ticket: Mapped["Ticket"] = relationship("Ticket", back_populates="predictions")
