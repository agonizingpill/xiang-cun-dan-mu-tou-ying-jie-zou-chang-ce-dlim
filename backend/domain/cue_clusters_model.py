from sqlalchemy import Boolean, CheckConstraint, Column, Float, ForeignKey, Integer, JSON, String, Table

from core.db import metadata


cue_clusters = Table('cue_clusters', metadata,
    Column('code', String(64), primary_key=True),
    Column('track', String(160), ForeignKey('cue_tracks.code'), nullable=False),
    Column('representative', String(160), ForeignKey('cue_tracks.code'), nullable=False),
    Column('distance', Float, nullable=False),
    Column('members', JSON, nullable=False),
    Column('token', String(64), nullable=False, unique=True),
)

cue_cluster_rules = Table('cue_cluster_rules', metadata,
    Column('code', String(64), primary_key=True),
    Column('rule', String(32), nullable=False),
    Column('trial', String(160), nullable=True),
)

cue_rule_trials = Table('cue_rule_trials', metadata,
    Column('code', String(64), primary_key=True),
    Column('token', String(64), nullable=False, unique=True),
    Column('baseline', String(32), nullable=False),
    Column('candidate', String(32), nullable=False),
    Column('verdict', String(32), nullable=False),
    Column('published', Boolean, nullable=False),
    Column('material', JSON, nullable=False),
    Column('result', JSON, nullable=False),
)
