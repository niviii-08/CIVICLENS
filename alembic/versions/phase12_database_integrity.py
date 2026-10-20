"""Add Phase 12 Database Integrity Indexes and Complete Model Schema

Revision ID: phase12_database_integrity
Revises: phase10_policy_evaluation_schema
Create Date: 2026-10-20 21:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from backend.database.base import Base

revision: str = 'phase12_database_integrity'
down_revision: Union[str, Sequence[str], None] = 'phase10_policy_evaluation_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Ensure all application model tables exist and add performance and integrity indexes.
    Idempotent: checks existing tables and indexes to prevent collisions.
    """
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = set(inspector.get_table_names())

    # 1. Create any missing model tables from Base.metadata
    for table_name, table in Base.metadata.tables.items():
        if table_name not in existing_tables:
            table.create(bind=conn, checkfirst=True)

    # 2. Add performance & integrity indexes on critical civic tables
    inspector = sa.inspect(conn)
    existing_tables = set(inspector.get_table_names())

    indexes_to_create = [
        ("idx_historical_schemes_name", "historical_schemes", ["scheme_name"]),
        ("idx_budget_records_comp", "budget_records", ["scheme_id", "financial_year", "budget_stage"]),
        ("idx_policy_registry_code", "policy_registry", ["canonical_scheme_code"]),
        ("idx_civic_graph_nodes_entity", "civic_graph_nodes", ["entity_type"]),
        ("idx_civic_evidence_edges_rel", "civic_evidence_edges", ["relationship_type"]),
    ]

    for idx_name, tbl_name, cols in indexes_to_create:
        if tbl_name in existing_tables:
            existing_indexes = {idx["name"] for idx in inspector.get_indexes(tbl_name) if idx.get("name")}
            if idx_name not in existing_indexes:
                op.create_index(idx_name, tbl_name, cols, unique=False)


def downgrade() -> None:
    """
    Downgrade Phase 12 integrity indexes safely.
    """
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = set(inspector.get_table_names())

    indexes_to_drop = [
        ("idx_historical_schemes_name", "historical_schemes"),
        ("idx_budget_records_comp", "budget_records"),
        ("idx_policy_registry_code", "policy_registry"),
        ("idx_civic_graph_nodes_entity", "civic_graph_nodes"),
        ("idx_civic_evidence_edges_rel", "civic_evidence_edges"),
    ]

    for idx_name, tbl_name in indexes_to_drop:
        if tbl_name in existing_tables:
            existing_indexes = {idx["name"] for idx in inspector.get_indexes(tbl_name) if idx.get("name")}
            if idx_name in existing_indexes:
                op.drop_index(idx_name, table_name=tbl_name)
