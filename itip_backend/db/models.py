from sqlalchemy import Column, String, Integer, ForeignKey, CheckConstraint, text, Index
from sqlalchemy.dialects.postgresql import UUID, DOUBLE_PRECISION, JSONB, TIMESTAMP
from geoalchemy2 import Geometry
from sqlalchemy.orm import relationship

try:
    from itip_backend.db.session import Base
except ImportError:  # pragma: no cover
    from db.session import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    username = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False) # 'public', 'emergency_authority', 'facility_operator', 'admin'
    osm_facility_id = Column(String(255))
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))

class ThermalEntity(Base):
    __tablename__ = 'thermal_entities'
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    geom = Column(Geometry('POINT', srid=4326), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))

    detections = relationship("Detection", back_populates="entity")
    profile = relationship("ThermalEntityProfile", uselist=False, back_populates="entity")
    classifications = relationship("Classification", back_populates="entity")
    candidate_facilities = relationship("CandidateFacility", back_populates="entity")

class Detection(Base):
    __tablename__ = 'detections'
    id = Column(UUID(as_uuid=True), server_default=text("gen_random_uuid()"), primary_key=True)
    entity_id = Column(UUID(as_uuid=True), ForeignKey('thermal_entities.id'))
    api_source = Column(String(50), nullable=False)
    satellite = Column(String(50), nullable=False)
    observed_at = Column(TIMESTAMP(timezone=True), nullable=False, primary_key=True) # needed for timescaledb
    latitude = Column(DOUBLE_PRECISION, nullable=False)
    longitude = Column(DOUBLE_PRECISION, nullable=False)
    geom = Column(Geometry('POINT', srid=4326), nullable=False)
    frp = Column(DOUBLE_PRECISION)
    brightness = Column(DOUBLE_PRECISION)
    confidence_score = Column(DOUBLE_PRECISION)
    confidence_label = Column(String(50))
    day_night_flag = Column(String(10))
    raw_payload = Column(JSONB)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))

    entity = relationship("ThermalEntity", back_populates="detections")
    
    __table_args__ = (
        CheckConstraint('confidence_score >= 0.0 AND confidence_score <= 1.0', name='check_conf_score'),
        Index('idx_detections_geom', geom, postgresql_using='gist'),
        Index('uq_detection_natural_key', api_source, observed_at, latitude, longitude, satellite, unique=True),
    )

class OSMInfrastructure(Base):
    __tablename__ = 'osm_infrastructure'
    osm_id = Column(String(255), primary_key=True)
    osm_type = Column(String(50), primary_key=True)
    geom = Column(Geometry('GEOMETRY', srid=4326), nullable=False)
    tags = Column(JSONB)
    retired_at = Column(TIMESTAMP(timezone=True))
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))

class CandidateFacility(Base):
    __tablename__ = 'candidate_facilities'
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    entity_id = Column(UUID(as_uuid=True), ForeignKey('thermal_entities.id'))
    osm_id = Column(String(255), nullable=False)
    osm_type = Column(String(50), nullable=False)
    distance_meters = Column(DOUBLE_PRECISION, nullable=False)
    probability = Column(DOUBLE_PRECISION)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))

    entity = relationship("ThermalEntity", back_populates="candidate_facilities")

class ThermalEntityProfile(Base):
    __tablename__ = 'thermal_entity_profiles'
    entity_id = Column(UUID(as_uuid=True), ForeignKey('thermal_entities.id'), primary_key=True)
    active_days_30 = Column(Integer)
    active_days_365 = Column(Integer)
    recurrence_rate_365 = Column(DOUBLE_PRECISION)
    median_frp = Column(DOUBLE_PRECISION)
    frp_iqr = Column(DOUBLE_PRECISION)
    day_night_ratio = Column(DOUBLE_PRECISION)
    regularity_score = Column(DOUBLE_PRECISION)
    baseline_status = Column(String(50))
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))

    entity = relationship("ThermalEntity", back_populates="profile")

class Classification(Base):
    __tablename__ = 'classifications'
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    entity_id = Column(UUID(as_uuid=True), ForeignKey('thermal_entities.id'))
    model_name = Column(String(255), nullable=False)
    model_version = Column(String(50), nullable=False)
    feature_version = Column(String(50), nullable=False)
    prediction = Column(String(100), nullable=False)
    confidence = Column(DOUBLE_PRECISION)
    probabilities = Column(JSONB, nullable=False)
    classified_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))

    entity = relationship("ThermalEntity", back_populates="classifications")
