import os
import io
from os.path import abspath
import pytest
from flask import Flask, session
from app import create_app, get_report_data, COL_CK, COL_COUNTRY, COL_STATE
from data import clear_data_storage
from pathlib import Path
import json
from csv import Sniffer
import pandas


@pytest.fixture
def client():
    global report_data
    app = create_app()

    with app.test_client() as client:
        yield client


def test_no_file_uploaded(client):
    rv = client.get('/data')
    assert b'An error was encountered: No data to query from, please upload a valid csv/json data file' in rv.data


def test_file_uploaded(client):
    rv = _upload_daily_report_file(client)
    report_data = get_report_data()  # must be called only after a request has been made
    assert b'CSV File uploaded successfully' in rv.data
    assert report_data.get_data() is not None


def _upload_daily_report_file(client):
    file = open(abspath('data/test_daily_report.csv'), "rb")
    data = {}
    data["file"] = file

    return client.post('/', data=data, content_type="multipart/form-data")


def _query_reponse_to_dataframe(data):
    return pandas.DataFrame.from_dict(json.load(io.BytesIO(data)))


def test_query_by_country(client):
    _upload_daily_report_file(client)

    rv = client.get('/data?country=Canada')
    df = _query_reponse_to_dataframe(rv.data)

    assert (all(c == 'Canada' for c in df[COL_COUNTRY]))
    assert len(df[COL_COUNTRY]) == 16


def test_query_by_state(client):
    _upload_daily_report_file(client)

    rv = client.get('/data?state=Yukon')
    df = _query_reponse_to_dataframe(rv.data)

    assert (all(s == 'Yukon' for s in df[COL_STATE]))
    assert len(df[COL_STATE]) == 1


def test_query_by_ck(client):
    _upload_daily_report_file(client)

    rv = client.get('/data?ck=Yukon, Canada')
    df = _query_reponse_to_dataframe(rv.data)

    assert (all(s == 'Yukon, Canada' for s in df[COL_CK]))
    assert len(df[COL_STATE]) == 1


def test_query_by_country_and_state(client):
    _upload_daily_report_file(client)

    rv = client.get('/data?country=Canada&state=Yukon')
    df = _query_reponse_to_dataframe(rv.data)

    assert (all(s == 'Yukon' for s in df[COL_STATE]))
    assert len(df[COL_STATE]) == 1


def test_query_by_country_state_ck(client):
    _upload_daily_report_file(client)

    rv = client.get('/data?country=Canada&state=Yukon&ck=Yukon, Canada')
    df = _query_reponse_to_dataframe(rv.data)

    assert (all(s == 'Yukon, Canada' for s in df[COL_CK]))
    assert len(df[COL_STATE]) == 1


def test_invalid_query(client):
    _upload_daily_report_file(client)

    rv = client.get('/data?country=blabla')
    df = _query_reponse_to_dataframe(rv.data)

    assert len(df) == 0


def test_csv_query(client):
    _upload_daily_report_file(client)
    rv = client.get('/data?country=Canada&csv=True')

    # checks if `sample` has row of columns
    assert Sniffer().has_header(sample=str(rv.data))
