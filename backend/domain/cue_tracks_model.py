from sqlalchemy import Boolean, CheckConstraint, Column, Float, ForeignKey, Integer, JSON, String, Table

from core.db import metadata


cue_tracks = Table('cue_tracks', metadata,
    Column('code', String(64), primary_key=True),
    Column('venue', String(160), ForeignKey('venues.code'), nullable=False),
    Column('timings', JSON, nullable=False),
    Column('shift', Float, nullable=False),
    Column('locked', Boolean, nullable=False),
)

cue_track_groups = Table('cue_track_groups', metadata,
    Column('track', String(160), ForeignKey('cue_tracks.code'), primary_key=True),
    Column('group', String(64), nullable=False),
)
