import pytest
from fetch_pernambucoaval import clean_local_string, clean_tipo_string, infer_tipo_from_hora


def test_clean_local_string_basic():
    s = "Grupo 12345 AVAL PE 11:00 HS ID Milhar Grupo Descricao"
    out = clean_local_string(s)
    assert 'Grupo' not in out
    assert 'AVAL' not in out.upper()
    assert 'ID' not in out


def test_clean_tipo_string_keywords():
    assert clean_tipo_string('manhã') == 'Diurno'
    assert clean_tipo_string('TARDE') == 'Vespertino'
    assert clean_tipo_string('noite') == 'Noturno'


def test_infer_tipo_from_hora():
    assert infer_tipo_from_hora('06:30') == 'Diurno'
    assert infer_tipo_from_hora('13:00') == 'Vespertino'
    assert infer_tipo_from_hora('20:15') == 'Noturno'
