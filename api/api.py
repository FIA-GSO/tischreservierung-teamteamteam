import flask
from flask import request   # wird benötigt, um die HTTP-Parameter abzufragen
from flask import jsonify   # übersetzt python-dicts in json
import sqlite3
import random
import string
import re

app = flask.Flask(__name__)
app.config["DEBUG"] = True  # Zeigt Fehlerinformationen im Browser, statt nur einer generischen Error-Message

@app.route('/', methods=['GET'])
def home():
    return "<h1>Tischreservierung</h1>"




# Anfang Reservierung

@app.route('/reservierung/buchen', methods=['POST'])
def ReservierungBuchen():
        #http://127.0.0.1:5000/reservierung/buchen?tischnummer=2&zeitpunkt=2023-02-02T18:15:00Z
    tischnummer: str
    if 'tischnummer' in request.args:
        tischnummer = str(request.args['tischnummer'])
    else:
        return "Error: Es wurde keine gültige Tischnummer für die Reservierung angegeben."
    
    buchungsdatum: str
    if 'buchungsdatum' in request.args:
        buchungsdatum = str(request.args['buchungsdatum'])
    else:
        return "Error: Es wurde keine gültige Buchungsdatum für die Reservierung angegeben."
    
    datumValid = FormatÜberprüfung(buchungsdatum)
    if not datumValid:
        return "Error: Beim verarbeiten des Datums ist ein Fehler aufgetreten!\nÜberprüfen Sie Ihre Eingabe."
        
    datum = Umstellen_Zu_SqliteFormat(buchungsdatum)
    db = GetDatenbank()
    anfrageTischIstFrei = Anfrage_Erstellen_TischIstFrei(datum, tischnummer)

    istReserviert = db.execute(anfrageTischIstFrei).execute().fetchall()
    if istReserviert:
        return "Error: Tisch ist bereits reserviert."
    
    pin = Pin_Erstellen(4)

    tischBuchenQuery = Anfrage_Erstellen_TischReservieren(datum, tischnummer, pin)
    erfolgreich = db.execute(tischBuchenQuery).execute()

    if(erfolgreich):
        objekt = {"datum": buchungsdatum, "tischnummer": tischnummer, "pin": pin}
        return jsonify(objekt)
    return "Error: Buchung war nicht erfolgreich"


def Anfrage_Erstellen_TischIstFrei(datetime: str, tischnummer: str):
    query = '''SELECT storniert
FROM reservierungen
WHERE zeitpunkt = \'{0}\'
	AND tischnummer = {1}'''
    return query.format(datetime, tischnummer)

def Anfrage_Erstellen_TischReservieren(datetime: str, tischnummer: str, pin: str):
    query = '''INSERT INTO reservierungen (zeitpunkt, tischnummer, pin, storniert)
VALUES (\'{0}\', \'{1}\', \'{2}\', \'False\')'''
    return query.format(datetime, tischnummer, pin)

def FormatÜberprüfung(datetime: str):
    """
    Verändert einen DateTime-String so, dass der Zeitpunkt zur halben Stunde beginnt.
    2022-02-02T18:17:00 --> 2022-02-02T18:30:00
    """
    # Regex-Muster: https://regex101.com/r/pQfJWb/1
    regPatternMinutes = "(:[0-5][0-9](:[0-5][0-9])?)"
    result = re.search(regPatternMinutes, datetime)
    if(result == ":30:00"):
        return True
    return False

def Umstellen_Zu_SqliteFormat(zeitpunkt):
    regPattern = "T"
    sqlite_timestamp = re.sub(regPattern, " ", zeitpunkt)
    regPattern = "Z"
    sqlite_timestamp = re.sub(regPattern, "", sqlite_timestamp)
    return sqlite_timestamp

def Pin_Erstellen(length):
    digits = string.digits
    result_str = "".join(random.choice(digits) for i in range(length))
    print("Password of length ", length, "is:", result_str)
    
#Ende Reservierung

#Anfang Anfrage Tisch frei
@app.route('/reservierung/suchen', methods=['GET'])
def ReservierungSuchen():
    #http://127.0.0.1:5000/reservierung/suchen?terminDatum=2022-02-02-17-30-00
    terminDatum: str
    if 'terminDatum' in request.args:
        terminDatum = str(request.args['terminDatum'])
    else:
        return "Error: Es wurde kein gülitger Termin für die Reservierung angegeben."

    db = GetDatenbank()
    datum: str = ParseDatum(terminDatum)
    if not datum:
        return 'Error: Beim verarbeiten des Datums ist ein Fehler aufgetreten!\nÜbeprüfen Sie Ihre Angaben.'
    
    query = GetFreieTischeQuery(datum)
    if not query:
        return "Error: Beim verarbeiten der Anfrage ist ein Fehler aufgetreten!\nÜberprüfen Sie Ihre Angaben."
    
    freieTische = db.execute(query).fetchall()
    return jsonify(freieTische)

@app.route('/reservierung/anzeigen', methods=['GET'])
def GetReservierungen():
    db = GetDatenbank()
    all_Tische = db.execute('SELECT * FROM reservierungen;').fetchall()

    return jsonify(all_Tische)

@app.route('/reservierung/stornieren', methods=['DELETE'])
def ReservierungStornieren():
    pin: str
    if 'pin' in request.args:
        pin = str(request.args['pin'])
    else:
        return "Error: Es wurde keine gültige Pinnummer für die Reservierung angegeben."
    
    reservierungsnummer: str
    if 'reservierungsnummer' in request.args:
        reservierungsnummer= str(request.args['reservierungsnummer'])
    else:
        return "Error: Es wurde keine gültige Reservierungsnummer angegeben."

    db = GetDatenbank()
    query = 'SELECT storniert FROM reservierungen WHERE reservierungsnummer = \'' + reservierungsnummer + '\';'
    stornierenTische = db.execute(query).fetchall()
    
    #Benötigt Reservierungsnummer, pin
    return jsonify(stornierenTische)

def GetTischBuchenQuery(terminDatum: str, tischnummer: int):
    datum: str = ParseDatum(terminDatum)
    if not datum:
        return ''
    query = '''SELECT DISTINCT tischnummer FROM tische
WHERE tischnummer NOT IN (
SELECT tischnummer
FROM reservierungen
WHERE zeitpunkt = \'{0}\'
	AND storniert = \'False\');'''
    return query.format(datum)

def GetTischFreiAnDatumQuery(terminDatum: str, tischnummer: int):
    query = '''SELECT storniert
FROM reservierungen
WHERE zeitpunkt = \'{0}\'
	AND tischnummer = {1}'''
    return query.format(terminDatum, tischnummer)

def GetFreieTischeQuery(terminDatum: str):
    query = '''SELECT DISTINCT tischnummer FROM tische
WHERE tischnummer NOT IN (
SELECT tischnummer
FROM reservierungen
WHERE zeitpunkt = \'{0}\'
	AND storniert = \'False\');'''
    return query.format(terminDatum)

def ParseDatum(dateTime: str):
    """Überprüft, ob ein DateTime-String einem bestimmten Muster entspricht."""
    # Regex-Muster: https://regex101.com/r/xz7hfg/3
    regPatternInternetTimeFormat = "^[0-9]{4}-[0-1][0-9]-[0-3][0-9]T[0-2][0-9]:[0-5][0-9]:[0-5][0-9](.[0-9][0-9])?Z?"
    isInternetTimeFormat = re.search(regPatternInternetTimeFormat, dateTime)
    if isInternetTimeFormat:
        return True
    return False

def GetDatenbank():
    conn = sqlite3.connect('C:\\git\\tischreservierung-teamteamteam\\api\\buchungssystem.sqlite')
    cur = conn.cursor()
    return cur

app.run()