from flask import Flask, request, g
import pandas
from json import dumps
from data import ReportData, clear_data_storage

ALLOWED_EXTENSIONS = ['csv']
COL_COUNTRY = 'Country_Region'
COL_STATE = 'Province_State'
COL_CK = 'Combined_Key'
REQUIRED_COLUMNS = [COL_CK, COL_COUNTRY, COL_STATE]


def get_report_data():
    if 'report_data' not in g:
        g.report_data = ReportData()
    return g.report_data


def create_app():
    app = Flask(__name__)
    log = app.logger.info
    logerr = app.logger.error

    clear_data_storage()

    @app.route("/data", methods=['GET'])
    def query_data():
        """Endpoint for data queries

        Query params:
            `country`: country (Country_Region) to filter data 
            `state`: state (Province_State) to filter data
            `ck`: combined key (Combined_Key) to filter data

            To specify multiple values of each query parameter use comma separation. 
            Ex. `/data?country=India,China`

            Note for `ck` there can only be one value

            `csv` (True | False): Whether to send data in json or csv format

        """
        report_data = get_report_data()

        def _get_query_values(key):
            value = request.args.get(key)
            if value:
                return value.split(',')
            return None

        countries = _get_query_values('country')
        states = _get_query_values('state')
        cks = request.args.get('ck')
        cks = cks and [cks]
        _output_csv = _get_query_values('csv')
        output_csv = _output_csv and _output_csv[0] == 'True'

        log(f'countries: {countries}')
        log(f'states: {states}')
        log(f'combined_keys: {cks}')
        log(f'csv: {output_csv}')

        df = report_data.get_data()

        if df is None:
            return _error_response("No data to query from, please upload a valid csv/json data file")

        if countries:
            df = df[df[COL_COUNTRY].isin(countries)]

        if states:
            df = df[df[COL_STATE].isin(states)]

        if cks:
            df = df[df[COL_CK].isin(cks)]

        if output_csv:
            return df.to_csv()
        else:
            return df.to_json()

    @app.route("/", methods=['POST'])
    def upload_csv_file():
        report_data = get_report_data()
        file = request.files['file']
        if not file:
            return _error_response("No file part in the request body")
        filename = file.filename
        if filename == '' and not _allowed_file(filename):
            return _error_response("No file uploaded")

        log("csv file uploaded")

        file_stream = file.stream
        df = pandas.read_csv(file_stream)
        columns = df.columns

        if not _valid_csv_columns(columns):
            return _bad_csv_format(f'Missing required columns: {dumps(REQUIRED_COLUMNS)}')

        log("csv file is valid")

        try:
            log(df)
            report_data.update_data(df)
        except Exception as e:
            logerr(e)
            return _error_response('Storing csv data')

        return "CSV File uploaded successfully"

    return app


def _valid_csv_columns(columns):
    return set(columns).intersection(set(REQUIRED_COLUMNS)) == set(REQUIRED_COLUMNS)


def _allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def _error_response(msg, code=500):
    return f'An error was encountered: {msg}', code


def _bad_csv_format(msg):
    return _error_response(f'Bad csv format: {msg}', 500)


if __name__ == '__main__':
    create_app().run()
