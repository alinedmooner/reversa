# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Unit tests del grafo del dinero y el recall camt.056 en ambos rieles."""

import copy

import pytest

from app import money_graph
from app.money_graph import trace_funds
from app.recall import issue_recall


@pytest.fixture(autouse=True)
def _reset_graph():
    """Aísla el estado por-proceso del grafo (flags blocked) entre tests."""
    snapshot = copy.deepcopy(money_graph.MONEY_GRAPH)
    yield
    money_graph.MONEY_GRAPH.clear()
    money_graph.MONEY_GRAPH.update(snapshot)


def test_trace_breb_chain_three_hops_cop():
    result = trace_funds("3001234567")
    assert result["hops"] == 3
    assert result["currency"] == "COP"
    assert result["current_location"]["key"] == "3155551234"
    assert result["status"] == "FONDOS DETENIDOS - interceptable"


def test_trace_pix_chain_three_hops_brl():
    result = trace_funds("123.456.789-09")
    assert result["hops"] == 3
    assert result["currency"] == "BRL"
    # CPF -> celular -> chave aleatória (EVP)
    assert result["current_location"]["key"] == "7f3a9c2e-4b8d-4f6a-9e1c-2d5b8a7c4e3f"
    assert result["status"] == "FONDOS DETENIDOS - interceptable"


def test_recall_pix_emits_brl_camt056():
    result = issue_recall("7f3a9c2e-4b8d-4f6a-9e1c-2d5b8a7c4e3f", 50000)
    assert result["status"] == "BLOQUEO EMITIDO"
    assert result["currency"] == "BRL"
    assert 'Ccy="BRL"' in result["camt_056"]
    assert "<Cd>FRAD</Cd>" in result["camt_056"]


def test_recall_breb_emits_cop_camt056():
    result = issue_recall("3155551234", 11000000)
    assert result["currency"] == "COP"
    assert 'Ccy="COP"' in result["camt_056"]


def test_recall_marks_blocked_and_second_recall_is_noop():
    issue_recall("3155551234", 11000000)
    assert trace_funds("3001234567")["status"].startswith("FONDOS BLOQUEADOS")
    again = issue_recall("3155551234", 11000000)
    assert again["status"] == "YA BLOQUEADA"


def test_unknown_key_is_reported():
    assert issue_recall("0000000000", 1)["status"] == "ERROR"
    assert "fuera del grafo" in trace_funds("0000000000")["status"]
