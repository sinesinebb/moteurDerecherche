# tests/unit/test_elasticsearch_indexer.py
import pytest
from unittest import mock
import importlib

es_mod = importlib.import_module("src.processors.elasticsearch_indexer")


def test__parse_hosts_default_when_none():
    hosts = es_mod._parse_hosts(None)
    assert isinstance(hosts, list)
    assert hosts[0].startswith("http://")


def test_doc_to_action_with_embedding_in_dict():
    doc = {"text": "hello", "metadata": {"u": "x"}, "id": "abc", "embedding": [0.1, 0.2, 0.3]}
    act = es_mod._doc_to_action("idx", doc, id_field=None, vector_field_name="vec")
    assert act["_index"] == "idx"
    assert act["_source"]["text"] == "hello"
    assert act["_source"]["metadata"]["u"] == "x"
    assert "vec" in act["_source"]
    assert act["_source"]["vec"] == [0.1, 0.2, 0.3]
    assert act["_id"] == "abc"


def test_doc_to_action_with_embedding_attribute():
    class D:
        def __init__(self):
            self.text = "t"
            self.metadata = {}
            self.embedding = [1.0, 2.0]

    d = D()
    act = es_mod._doc_to_action("idx", d, id_field=None, vector_field_name="vec")
    assert act["_source"]["vec"] == [1.0, 2.0]


def test_index_documents_bulk_calls_helpers_and_passes_vector(monkeypatch):
    fake_client = mock.MagicMock()

    def fake_bulk(client_arg, actions_iter, chunk_size=500, raise_on_error=False):
        actions_list = list(actions_iter)
        assert actions_list, "no actions produced"
        found_vec = any("vec" in a.get("_source", {}) for a in actions_list)
        assert found_vec, "vector field 'vec' not found in produced actions"
        return (len(actions_list), [])

    fake_helpers = mock.MagicMock()
    fake_helpers.bulk.side_effect = fake_bulk
    monkeypatch.setattr(es_mod, "helpers", fake_helpers)

    docs = [
        {"text": "t1", "embedding": [0.1, 0.2]},
        {"text": "t2", "embedding": [0.3, 0.4]},
    ]
    res = es_mod.index_documents_bulk(fake_client, index_name="idx", docs=docs, chunk_size=2, vector_field_name="vec")
    assert isinstance(res, dict)
    assert res["success"] == 2


def test_index_documents_bulk_with_vector_dims_success(monkeypatch):
    fake_client = mock.MagicMock()

    def fake_bulk(client_arg, actions_iter, chunk_size=500, raise_on_error=False):
        actions_list = list(actions_iter)
        return (len(actions_list), [])

    fake_helpers = mock.MagicMock()
    fake_helpers.bulk.side_effect = fake_bulk
    monkeypatch.setattr(es_mod, "helpers", fake_helpers)

    docs = [
        {"text": "t1", "embedding": [0.1, 0.2]},
        {"text": "t2", "embedding": [0.3, 0.4]},
    ]
    res = es_mod.index_documents_bulk(fake_client, index_name="idx", docs=docs, chunk_size=2, vector_field_name="vec", vector_dims=2)
    assert res["success"] == 2


def test_index_documents_bulk_with_vector_dims_mismatch_raises():
    fake_client = mock.MagicMock()
    docs = [
        {"text": "t1", "embedding": [0.1, 0.2, 0.3]},  # length 3, expected 2
    ]
    with pytest.raises(ValueError):
        es_mod.index_documents_bulk(fake_client, index_name="idx", docs=docs, vector_field_name="vec", vector_dims=2)


def test_index_documents_bulk_with_vector_dims_mismatch_non_strict(monkeypatch):
    fake_client = mock.MagicMock()

    def fake_bulk(client_arg, actions_iter, chunk_size=500, raise_on_error=False):
        actions_list = list(actions_iter)
        # since strict=False and embedding is invalid, actions shouldn't contain 'vec'
        assert all("vec" not in a.get("_source", {}) for a in actions_list)
        return (len(actions_list), [])

    fake_helpers = mock.MagicMock()
    fake_helpers.bulk.side_effect = fake_bulk
    monkeypatch.setattr(es_mod, "helpers", fake_helpers)

    docs = [
        {"text": "t1", "embedding": [0.1, 0.2, 0.3]},  # length 3, expected 2
    ]
    # Should not raise, but omit vector field
    res = es_mod.index_documents_bulk(fake_client, index_name="idx", docs=docs, vector_field_name="vec", vector_dims=2, strict=False)
    assert res["success"] == 1
