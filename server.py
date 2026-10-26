import json
import os 
from datetime import datetime
from flask import Flask,render_template,request,redirect,flash,url_for

club_bookings = {}

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

@app.route('/showSummary', methods=['POST'])
def showSummary():
    try:
        club = [c for c in clubs if c['email'] == request.form['email']][0]
        return render_template('welcome.html', club=club, competitions=competitions, bookings=club_bookings.get(club['name'], {}))
    except Exception:
        flash("Something went wrong, please try again.")
        return render_template('index.html')
    
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
        
        if placesRequired <= 0:
            flash("You must book a positive number of places!")
            return render_template('welcome.html', club=club, competitions=competitions, bookings=club_bookings.get(club['name'], {}))
            
        competition_date = datetime.strptime(competition['date'], '%Y-%m-%d %H:%M:%S')
        if competition_date < datetime.now():
            flash("You cannot book places for a past competition!")
            return render_template('welcome.html', club=club, competitions=competitions, bookings=club_bookings.get(club['name'], {}))

        # Récupérer ce que le club a déjà réservé pour cette compétition
        current_booked = club_bookings.get(club['name'], {}).get(competition['name'], 0)
        total_requested = current_booked + placesRequired

        # 1. Vérification du maxbooking cumulé (max 12 places au total par club/compétition)
        if total_requested > 12:
            flash(f"You cannot have more than 12 places total for a competition! (Already booked: {current_booked})")
            return render_template('welcome.html', club=club, competitions=competitions, bookings=club_bookings.get(club['name'], {}))
        
        # 2. Vérification des points du club
        if placesRequired > int(club['points']):
            flash("Not enough points available!")
            return render_template('welcome.html', club=club, competitions=competitions, bookings=club_bookings.get(club['name'], {}))

        # 3. Vérification du stock global de la compétition
        if placesRequired > int(competition['numberOfPlaces']):
            flash("Not enough places available in this competition!")
            return render_template('welcome.html', club=club, competitions=competitions, bookings=club_bookings.get(club['name'], {}))

        # Mise à jour
        competition['numberOfPlaces'] = int(competition['numberOfPlaces']) - placesRequired
        club['points'] = int(club['points']) - placesRequired

        if club['name'] not in club_bookings:
            club_bookings[club['name']] = {}

        club_bookings[club['name']][competition['name']] = total_requested

        flash(f'Great-booking complete! You have successfully booked {placesRequired} places.')
        return render_template('welcome.html', club=club, competitions=competitions, bookings=club_bookings[club['name']])
    except Exception:
        flash("Something went wrong, please try again.")
        return render_template('welcome.html', club=club, competitions=competitions, bookings=club_bookings.get(club['name'], {}))
    
  #ANNULATION D'UNE RÉSERVATION#
@app.route('/cancelBooking', methods=['POST'])
def cancelBooking():
    try:
        competition = [c for c in competitions if c['name'] == request.form['competition']][0]
        club = [c for c in clubs if c['name'] == request.form['club']][0]
        placesToCancel = int(request.form['places'])
        
        # Vérifier si le club a des réservations pour cette compétition
        if club['name'] in club_bookings and competition['name'] in club_bookings[club['name']]:
            booked_places = club_bookings[club['name']][competition['name']]
            
            if 0 < placesToCancel <= booked_places:
                # Mettre à jour le suivi des réservations
                club_bookings[club['name']][competition['name']] -= placesToCancel
                if club_bookings[club['name']][competition['name']] == 0:
                    del club_bookings[club['name']][competition['name']]
                
                # Restituer les places à la compétition et les points au club
                competition['numberOfPlaces'] = int(competition['numberOfPlaces']) + placesToCancel
                club['points'] = int(club['points']) + placesToCancel
                
                flash(f'Booking cancelled successfully : {placesToCancel} places returned.')
            else:
                flash("Invalid number of places to cancel.")
        else:
            flash("No booking found for this competition.")
            
        return render_template('welcome.html', club=club, competitions=competitions, bookings=club_bookings.get(club['name'], {}))
    except Exception:
        flash("An error occurred while cancelling the booking.")
        return render_template('welcome.html', club=club, competitions=competitions, bookings=club_bookings.get(club['name'], {}))    
    
@app.route('/points')
def show_clubs_points():
    return render_template('point_tables.html', clubs=clubs)


@app.route('/logout')
def logout():
    return redirect(url_for('index'))