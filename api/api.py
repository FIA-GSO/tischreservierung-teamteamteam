from flask import Flask
from flask import request   # wird benötigt, um die HTTP-Parameter abzufragen
from flask import jsonify   # übersetzt python-dicts in json
import sqlite3
import random
import re


def init_app(app):
    @app.route('/', methods=['GET'])
    def home():
        return "<h1>Tischreservierung</h1>"

    @app.route('/v1/reservierungen', methods=['GET'])
    def reservierung_suchen():
        # http://127.0.0.1:5000/reservierung/suchen?terminDatum=2023-02-02T18:15:00Z
        datum: str
        if 'datum' in request.args:
            datum = str(request.args['datum'])
        else:
            return get_all_reservierungen()

        datumParsed = parse_date_to_sqlite(datum)
        if datumParsed is None:
            return 'Error: Beim verarbeiten des Datums ist ein Fehler aufgetreten!\nÜbeprüfen Sie Ihre Angaben.'

        db = get_db_connection()

        query = get_free_tables_query(datumParsed)
        if not query:
            return "Error: Beim verarbeiten der Anfrage ist ein Fehler aufgetreten!\nÜberprüfen Sie Ihre Angaben."

        freeTables = db.cursor().execute(query).fetchall()
        return jsonify(freeTables)

    @app.route('/v1/reservierungen', methods=['POST'])
    def reservierung_buchen():
        # http://127.0.0.1:5000/reservierung/buchen?tischnummer=2&datum=2023-02-02T18:15:00Z
        tischnummer: str
        if 'tischnummer' in request.args:
            tischnummer = str(request.args['tischnummer'])
        else:
            return "Error: Es wurde keine gültige Tischnummer für die Reservierung angegeben."

        datum: str
        if 'datum' in request.args:
            datum = str(request.args['datum'])
        else:
            return "Error: Es wurde keine gültige Buchungsdatum für die Reservierung angegeben."

        datumParsed = parse_date_to_sqlite(datum)
        if not datumParsed:
            return 'Error: Beim verarbeiten des Datums ist ein Fehler aufgetreten!\nÜbeprüfen Sie Ihre Angaben.'

        db = get_db_connection()
        freeTableQuery = get_table_is_free_query(datumParsed, tischnummer)

        isReserved = db.cursor().execute(freeTableQuery).fetchall()
        if isReserved:
            return "Error: Tisch ist bereits reserviert."

        pin = generate_pin(4)

        reserveQuery = get_tisch_reserve_query(datumParsed, tischnummer, pin)
        success = db.cursor().execute(reserveQuery)

        db.commit()

        if success:
            objekt = {"datum": datum, "tischnummer": tischnummer, "pin": pin}
            return jsonify(objekt)
        return "Error: Buchung war nicht erfolgreich"

    @app.route('/v1/reservierungen', methods=['DELETE'])
    def cancel_reservierung():
        return "Error: Nicht implementiert"


def create_app():
    app = Flask(__name__)
    init_app(app=app)
    # Zeigt Fehlerinformationen im Browser, statt nur einer generischen Error-Message
    app.config["DEBUG"] = True
    return app

# @app.route('/v1/reservierungen', methods=['GET'])


def get_all_reservierungen():
    db = get_db_connection()
    all_Tische = db.cursor().execute('SELECT * FROM reservierungen;').fetchall()

    return jsonify(all_Tische)


def parse_date_to_sqlite(datum: str):
    datumValid = check_date_format(datum)
    if datumValid == False:
        return None

    datumParsed = parse_to_sqlite_format(datum)
    return datumParsed


def check_date_format(dateTime: str):
    regPatternInternetTimeFormat = "^[0-9]{4}-[0-1][0-9]-[0-3][0-9]T[0-2][0-9]:[0-5][0-9]:[0-5][0-9](.[0-9][0-9])?Z?"
    isInternetTimeFormat = re.search(regPatternInternetTimeFormat, dateTime)
    if isInternetTimeFormat:
        return True
    return False


def check_date_end_with_30_min(datetime: str):
    regPatternMinutes = "(:[0-5][0-9](:[0-5][0-9])?)"
    result = re.search(regPatternMinutes, datetime)
    if (result == ":30:00"):
        return True
    return False


def parse_to_sqlite_format(zeitpunkt):
    regPattern = "T"
    sqlite_timestamp = re.sub(regPattern, " ", zeitpunkt)
    regPattern = "Z"
    sqlite_timestamp = re.sub(regPattern, "", sqlite_timestamp)
    print(sqlite_timestamp)
    return sqlite_timestamp


def get_table_is_free_query(datetime: str, tischnummer: str):
    query = '''SELECT storniert
FROM reservierungen
WHERE zeitpunkt = \'{0}\'
	AND tischnummer = \'{1}\''''
    return query.format(datetime, tischnummer)


def get_tisch_reserve_query(datetime: str, tischnummer: str, pin: str):
    query = '''INSERT INTO reservierungen (zeitpunkt, tischnummer, pin, storniert)
VALUES (\'{0}\', \'{1}\', \'{2}\', \'False\')'''
    return query.format(datetime, tischnummer, pin)


def generate_pin(length):
    return random.randint(1000, 9999)


def get_free_tables_query(terminDatum: str):
    query = '''SELECT DISTINCT tischnummer FROM tische
WHERE tischnummer NOT IN (
SELECT tischnummer
FROM reservierungen
WHERE zeitpunkt = \'{0}\'
	AND storniert = \'False\');'''
    return query.format(terminDatum)


def get_db_connection():
    conn = sqlite3.connect('buchungssystem.sqlite')
    return conn


if __name__ == "__main__":
    app = create_app()
    app.run()
