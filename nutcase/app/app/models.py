from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from datetime import datetime, timezone

from app import db

from enum import Enum

Log_Level = Enum("Log_Level", ["info", "warning", "alert"])
Log_Category = Enum("Log_Category", ["Comms", "Power", "Battery", "Other"])

class LogEntry(db.Model):
    __tablename__ = 'logentry'
    id:             so.Mapped[int]                = so.mapped_column(primary_key=True)
    time_first:     so.Mapped[Optional[datetime]] = so.mapped_column(default = lambda: datetime.now(timezone.utc))
    time_latest:    so.Mapped[Optional[datetime]] = so.mapped_column(default = lambda: datetime.now(timezone.utc))
    occurrences:    so.Mapped[int]                = so.mapped_column(default = 1)
    level:          so.Mapped[int]                = so.mapped_column(default = Log_Level.info.value)
    title:          so.Mapped[str]                = so.mapped_column(sa.String(128), index=True, unique=False)
    detail:         so.Mapped[str]                = so.mapped_column(sa.String(512), index=True, unique=False, nullable=True)
    server:         so.Mapped[str]                = so.mapped_column(sa.String(128), index=True, unique=False, nullable=True)
    device:         so.Mapped[str]                = so.mapped_column(sa.String(128), index=True, unique=False, nullable=True)
    category:       so.Mapped[int]                = so.mapped_column(index=True, unique=False, default=Log_Category.Other.value)
    read:           so.Mapped[bool]               = so.mapped_column(unique = False, default=False)

    def __repr__(self):
        return '<LogEntry {}>'.format(self.id)

    def __str__(self):
        return f"{self.title}, {self.level}, {self.category}, {self.device}"
