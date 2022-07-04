#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.secret_key = 'a new hope'
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Stupid13@localhost:5432/fyyur'
# make things slightly faster
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

migrate = Migrate(app, db)

#----------------------------------------------------------------------------#A
# Models.
#----------------------------------------------------------------------------#
class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description= db.Column(db.String(120))
    genres = db.Column(db.String(120))
    shows = db.relationship("Show", backref="Venue", lazy=True)
    def __repr__(self):
      return f'<Venue id: {self.id}, name: {self.name}, city: {self.city}, state: {self.state}, seeking_talent: {self.seeking_talent}>'


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description= db.Column(db.String(120))
    shows = db.relationship("Show", backref="Artist", lazy=True)

    def __repr__(self):
      return f'<ARTIST id: {self.id}, name: {self.name}, city: {self.city}, state: {self.state}>'

class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
      return f'<Show artist_id: {self.artist_id}, venue_id: {self.venue_id}, start_time: {self.start_time}>'

db.create_all()
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  if isinstance(value, str):
      date = dateutil.parser.parse(value)
  else:
      date = value
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  data = []
  areas = db.session.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state)
  for area in areas:
    venues = Venue.query.filter(Venue.city == area.city, Venue.state == area.state).all()
    venue_data = []
    for ven in venues:
      venue_data.append({
        "id": ven.id,
        "name": ven.name
      })
    data.append({
      "city":area.city,
      "state":area.state,
      "venues":venue_data
    })

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  venues = Venue.query.filter(Venue.name.like(f'%{request.form.get("search_term")}%')).all()
  data = []
  for venue in venues:
    data.append({
      "id": venue.id,
      "name": venue.name
    })

  response={
    "count": len(venues),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  current_date = datetime.datetime.now()
  upcoming_shows = []
  past_shows = []
  venue = Venue.query.get({"id": venue_id}) 
  for show in venue.shows:
    artist = Artist.query.get({"id": show.artist_id})
    if current_date > show.start_time:
      upcoming_shows.append({
        "artist_id": show.artist_id,
        "start_time": show.start_time,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link
      })
    else:
      past_shows.append({
        "artist_id": show.artist_id,
        "start_time": show.start_time,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link
      })

  artist_data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres.replace("{","").replace("}","").split(","),
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
 
  return render_template('pages/show_venue.html', venue=artist_data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  try:
    new_venue = Venue(
      name = request.form.get('name'),
      city = request.form.get('city'),
      state = request.form.get('state'),
      address = request.form.get('address'),
      phone = request.form.get('phone'),
      image_link = request.form.get('image_link'),
      genres = request.form.getlist('genres'),
      facebook_link = request.form.get('facebook_link'),
      website = request.form.get('website_link'),
      seeking_talent = True  if request.form.get('seeking_talent') == 'y' else False,
      seeking_description = request.form.get('seeking_description')
    )
    db.session.add(new_venue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except Exception as e:
    print(e)
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be added')
    db.session.rollback()
  finally: 
    db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    # Delete the venue by it's id & update the db
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return None 

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  artists = Artist.query.filter(Artist.name.ilike(f'%{request.form.get("search_term")}%')).all()
  data = []
  for artist in artists:
    data.append({
        "id": artist.id,
        "name": artist.name
      })

  response={
    "count": len(artists),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  current_date = datetime.datetime.now()
  upcoming_shows = []
  past_shows = []
  artist = Artist.query.get({"id": artist_id})
  for show in artist.shows:
    venue = Venue.query.get({"id": show.venue_id})
    if current_date > show.start_time:
      upcoming_shows.append({
        "venue_id": show.venue_id,
        "start_time": show.start_time,
        "venue_name": venue.name,
        "venue_image_link": venue.image_link
      })
    else:
      past_shows.append({
        "venue_id": show.venue_id,
        "start_time": show.start_time,
        "venue_name": venue.name,
        "venue_image_link": venue.image_link
      })
  artist_data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres.replace("{","").replace("}","").split(","),
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }

  return render_template('pages/show_artist.html', artist=artist_data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get({"id": artist_id})
  artist_data = {
    "id": artist.id,
    "name": artist.name,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "image_link": artist.image_link,
    "genres": ','.join(artist.genres),
    "website_link": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description
  }

  form = ArtistForm(data=artist_data)

  return render_template('forms/edit_artist.html', form=form, artist=artist_data)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.get({"id": artist_id})
  error = False
  seeking_venue = True if request.form.get('seeking_venue') != None else False 
  try:
    artist.name = request.form.get("name")
    artist.city = request.form.get("city")
    artist.state = request.form.get("state")
    artist.phone = request.form.get("phone")
    artist.genres = ''.join(request.form.get("genres"))
    artist.website = request.form.get("website")
    artist.facebook_link = request.form.get("facebook_link")
    artist.image_link = request.form.get("image_link")
    artist.seeking_venue = seeking_venue
    artist.seeking_description = request.form.get("seeking_description")
    db.session.commit()
  except Exception as e:
    print(e)
    error = True
    db.session.rollback()
  finally:
    if not error:
      flash('Artist ' + request.form.get("name")+ ' was successfully updated!')
    else:
      flash('An error occurred. Artist ' + request.form.get("name")+ ' could not be updated.')
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))


  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get({"id": venue_id})
  venue_data={
    "id": venue.id,
    "name": venue.name,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "image_link": venue.image_link,
    "genres": ",".join(venue.genres),
    "address": venue.address,
    "website_link": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
  }

  form = VenueForm(data=venue_data)
  return render_template('forms/edit_venue.html', form=form, venue=venue_data)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue = Venue.query.get({"id": venue_id})
  error = False
  try:
    seeking_talent= True if request.form.get('seeking_talent') != None else False 
    venue.name = request.form.get("name")
    venue.city = request.form.get("city")
    venue.state = request.form.get("state")
    venue.phone = request.form.get("phone")
    venue.genres = ','.join(request.form.get("genres"))
    venue.address = request.form.get("address")
    venue.website = request.form.get("website")
    venue.facebook_link = request.form.get("facebook_link")
    venue.image_link = request.form.get("image_link")
    venue.seeking_talent = seeking_talent
    venue.seeking_description = request.form.get("seeking_description")
    db.session.commit()
  except Exception as e:
    print(e)
    error = True
    db.session.rollback()
  finally:
    if not error:
      flash('Venue ' + request.form.get("name") + ' was successfully updated!')
    else:
      flash('An error occurred. Venue ' + request.form.get("name") + ' could not be updated.')
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  try:
    new_artist = Artist(
      name = request.form.get('name'),
      city = request.form.get('city'),
      state = request.form.get('state'),
      phone = request.form.get('phone'),
      image_link = request.form.get('image_link'),
      genres = request.form.getlist('genres'),
      facebook_link = request.form.get('facebook_link'),
      website = request.form.get('website_link'),
      seeking_venue = True if request.form.get('seeking_venue') == 'y' else False,
      seeking_description = request.form.get('seeking_description')
    )
    db.session.add(new_artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except Exception as e:
    print(e)
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be added')
    db.session.rollback()
  finally: 
    db.session.close()
  return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------
@app.route('/show')
def show():
  return render_template("pages/show.html")

@app.route('/shows/search', methods=['POST'])
def search_shows():
  search_term = request.form.get("search_term")
  fuzzy_venue = db.session.query(Show).join(Venue, Show.venue_id == Venue.id).filter(Venue.name.ilike(f'%{search_term}%')).all()
  fuzzy_artist= db.session.query(Show).join(Artist, Show.artist_id == Artist.id).filter(Artist.name.ilike(f'%{search_term}%')).all()
  all_matches = []
  for show in fuzzy_venue:
    if show not in all_matches:
      all_matches.append(show)
  for show in fuzzy_artist:
    if show not in all_matches:
      all_matches.append(show)
  data = []
  for show in all_matches:
    data.append({
      "venue_id": show.venue_id, 
      "venue_name": show.Venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.Artist.name,
      "start_time": show.start_time,
      "artist_image_link": show.Artist.image_link
    })
  response={
    "count": len(data),
    "data": data
  }
  return render_template('pages/show.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  data = db.session.query(Show).join(Venue, Show.venue_id == Venue.id).join(Artist, Show.artist_id == Artist.id).all()
  resp = []
  for show in data:
    resp.append({
      "venue_id": show.venue_id, 
      "venue_name": show.Venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.Artist.name,
      "start_time": show.start_time,
      "artist_image_link": show.Artist.image_link
    })
  return render_template('pages/shows.html', shows=resp)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  try:
    new_show = Show(
      artist_id = request.form.get('artist_id'),
      venue_id = request.form.get('venue_id'),
      start_time = request.form.get('start_time'),
    )
    db.session.add(new_show)
    db.session.commit()
    flash('Show at ' + request.form['start_time'] + ' was successfully listed!')
  except Exception as e:
    print(e)
    flash('An error occurred. Show at ' + request.form['start_time'] + ' could not be added')
    db.session.rollback()
  finally: 
    db.session.close()
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
