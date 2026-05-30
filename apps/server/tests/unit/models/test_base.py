"""Unit tests for app.models.base document helpers."""
from __future__ import annotations

from datetime import UTC, datetime

from bson import ObjectId

from app.models import base


def test_utcnow_timezone_aware():
    now = base.utcnow()
    assert now.tzinfo is not None


def test_new_object_id_is_objectid():
    oid = base.new_object_id()
    assert isinstance(oid, ObjectId)


def test_serialize_doc_none():
    assert base.serialize_doc(None) is None


def test_serialize_doc_converts_ids_and_dates():
    oid = ObjectId()
    ref = ObjectId()
    dt = datetime(2024, 1, 1, tzinfo=UTC)
    doc = {"_id": oid, "owner_id": ref, "created_at": dt, "name": "x", "n": 5}

    out = base.serialize_doc(doc)
    assert out is not None
    assert out["id"] == str(oid)
    assert "_id" not in out
    assert out["owner_id"] == str(ref)
    assert out["created_at"] == dt.isoformat()
    assert out["name"] == "x"
    assert out["n"] == 5


def test_base_document_fields_has_timestamps():
    fields = base.base_document_fields()
    assert set(fields) == {"created_at", "updated_at"}
    assert fields["created_at"] == fields["updated_at"]
