import flask
from flask import request   # wird benötigt, um die HTTP-Parameter abzufragen
from flask import jsonify   # übersetzt python-dicts in json
import sqlite3

app = flask.Flask(__name__)
app.config["DEBUG"] = True  # Zeigt Fehlerinformationen im Browser, statt nur einer generischen Error-Message

@app.route('/', methods=['GET'])
def home():
    return "<h1>Tischreservierung</h1>"

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

@app.route('/reservierung/buchen', methods=['POST'])
def ReservierungBuchen():
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
    
    
    
    return 0

@app.route('/reservierung/suchen', methods=['GET'])
def ReservierungSuchen():
    #http://127.0.0.1:5000/reservierung/suchen?terminDatum=2023-02-02-17-30-00
    terminDatum: str
    if 'terminDatum' in request.args:
        terminDatum = str(request.args['terminDatum'])
    else:
        return "Error: Es wurde kein gülitger Termin für die Reservierung angegeben."

    db = GetDatenbank()
    query = GetFreieTischeQuery(terminDatum)
    freieTische = db.execute(query).fetchall()
    return jsonify(freieTische)

def GetFreieTischeQuery(terminDatum: str):
    splits = terminDatum.split("-")
    formatCount = 0
    datum: str = ""
    for datumString in splits:
        formatCount += 1
        if(formatCount < 3):
            datum += datumString + "-"
        elif (formatCount == 3):
            datum += datumString + " "
        elif(formatCount == 6):
            datum += datumString
        else:
            datum += datumString + ":"    

    query = '''SELECT DISTINCT tischnummer FROM tische
WHERE tischnummer NOT IN (
SELECT tischnummer
FROM reservierungen
WHERE zeitpunkt = \'{0}\'
	AND storniert = \'False\');'''
    return query.format(datum)

def GetDatenbank():
    conn = sqlite3.connect('C:\\git\\tischreservierung-teamteamteam\\api\\buchungssystem.sqlite')
    cur = conn.cursor()
    return cur

app.run()