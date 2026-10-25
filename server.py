import json
import os 
from datetime import datetime
from flask import Flask,render_template,request,redirect,flash,url_for


def loadClubs():
    with open('clubs.json') as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions


app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'something_special')

competitions = loadCompetitions()
clubs = loadClubs()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/showSummary',methods=['POST'])
def showSummary():
    club = [club for club in clubs if club['email'] == request.form['email']][0]
    return render_template('welcome.html',club=club,competitions=competitions)


@app.route('/book/<competition>/<club>')
def book(competition,club):
    foundClub = [c for c in clubs if c['name'] == club][0]
    foundCompetition = [c for c in competitions if c['name'] == competition][0]
    if foundClub and foundCompetition:
        return render_template('booking.html',club=foundClub,competition=foundCompetition)
    else:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    try:
        competition = [c for c in competitions if c['name'] == request.form['competition']][0]
        club = [c for c in clubs if c['name'] == request.form['club']][0]
        placesRequired = int(request.form['places'])
        
        # --- VÉRIFICATION DU NOMBRE DE PLACES (POSITIF) ---
        if placesRequired <= 0:
            flash("You must book a positive number of places!")
            return render_template('welcome.html', club=club, competitions=competitions)
        
        # --- VÉRIFICATION DE LA DATE DE LA COMPÉTITION ---
        competition_date = datetime.strptime(competition['date'], '%Y-%m-%d %H:%M:%S')
        if competition_date < datetime.now():
            flash("You cannot book places for a past competition!")
            return render_template('welcome.html', club=club, competitions=competitions)
        
        # --- LIMITE DES 12 PLACES ---
        if placesRequired > 12:
            flash("You cannot book more than 12 places!")
            return render_template('welcome.html', club=club, competitions=competitions)
        
        # --- RESTRICTION DES POINTS ---
        if placesRequired > int(club['points']):
            flash("Not enough points available!")
            return render_template('welcome.html', club=club, competitions=competitions)
        
        competition['numberOfPlaces'] = int(competition['numberOfPlaces']) - placesRequired
        club['points'] = int(club['points']) - placesRequired
        flash(f'Great-booking complete! You have successfully booked {placesRequired} places.')
        return render_template('welcome.html', club=club, competitions=competitions)
    except Exception:
        flash("Something went wrong, please try again.")
        return render_template('welcome.html', club=club, competitions=competitions)

# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))