#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import sys
import json
import dateutil.parser
import babel

from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import Form

import logging
from logging import Formatter, FileHandler
from forms import *

from models import db, create_app
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = create_app()
moment = Moment(app)
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
from models import Artist, Venue, Show
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

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
  regions = Venue.query.with_entities(Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()
  
  for region in regions:
    venues = Venue.query.filter_by(state = region.state).filter_by(city = region.city).all()
    venue_data = []

    for venue in venues:
      venue_data.append({
        'id': venue.id,
        'name': venue.name
      })

    data.append({
      'city': region.city,
      'state': region.state,
      'venues': venue_data
    })
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_string = request.form.get('search_term')
  print(search_string)
  results = Venue.query.filter(Venue.name.ilike('%' + search_string + '%')).all()
  
  data = []
  for result in results:
    data.append({
      'id': result.id,
      'name': result.name
    })

  response={
    "count": len(results),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)
  shows = Show.query.filter_by(venue_id = venue.id).join(Artist).all()

  past_shows = []
  upcoming_shows = []
  for show in shows:
    if show.date > datetime.now():
      upcoming_shows.append({
        'artist_id': show.artists.id,
        'artist_name': show.artists.name,
        'artist_image_link': show.artists.image_link,
        'start_time': str(show.date)
      })
    else:
      past_shows.append({
        'artist_id': show.artists.id,
        'artist_name': show.artists.name,
        'artist_image_link': show.artists.image_link,
        'start_time': str(show.date)
      })

  data = {
    'id': venue.id,
    'name': venue.name,
    'genres': venue.genres,
    'address': venue.address,
    'city': venue.city,
    'state': venue.state,
    'phone': venue.phone,
    'website': venue.website,
    'facebook_link': venue.facebook_link,
    'seeking_talent': venue.seeking_talent,
    'seeking_description': venue.seeking_description,
    'image_link': venue.image_link,
    'past_shows': past_shows,
    'upcoming_shows': upcoming_shows,
    'past_shows_count': len(past_shows),
    'upcoming_shows_count': len(upcoming_shows)
  }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  venue = Venue()
  error = False

  try:
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.phone = request.form['phone']
    venue.address = request.form['address']
    venue.genres = request.form.getlist('genres')
    venue.facebook_link = request.form['facebook_link']
    venue.website = request.form['website']
    venue.image_link = request.form['image_link']

    if request.form['seeking_talent'] == 'True':
      venue.seeking_talent = True
    else:
      venue.seeking_talent = False
    venue.seeking_description = request.form['seeking_description']

    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  if error:
    flash('An error occurred: Venue ' + request.form['name'] + ' could not be listed!')
    abort(500)
  else:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  error = False
  body = {}
  try:
    shows = Show.query.filter_by(venue_id = venue_id).all()
    venue = Venue.query.get(venue_id)
    for show in shows:
      db.session.delete(show)
    db.session.delete(venue)
    db.session.commit()
    body['url'] = url_for('index')
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    print('perfect')
    db.session.close()

  if error:
    flash('An error occurred: Venue could not be deleted!')
    abort(500)
  else:
    flash('Venue was successfully deleted!')
    print('here')
    return jsonify(body)

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  return render_template('pages/artists.html', artists=Artist.query.all())

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_string = request.form.get('search_term')
  results = Artist.query.filter(Artist.name.ilike('%' + search_string + '%')).all()

  data = []
  for result in results:
    data.append({
      'id': result.id,
      'name': result.name
    })
  response={
    "count": len(results),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get(artist_id)
  shows = Show.query.filter_by(artist_id = artist.id).join(Venue).all()

  past_shows = []
  upcoming_shows = []
  for show in shows:
    if show.date > datetime.now():
      upcoming_shows.append({
        'venue_id': show.venues.id,
        'venue_name': show.venues.name,
        'venue_image_link': show.venues.image_link,
        'start_time': str(show.date)
      })
    else:
      past_shows.append({
        'venue_id': show.venues.id,
        'venue_name': show.venues.name,
        'venue_image_link': show.venues.image_link,
        'start_time': str(show.date)
      })

  data = {
    'id': artist.id,
    'name': artist.name,
    'genres': artist.genres,
    'city': artist.city,
    'state': artist.state,
    'phone': artist.phone,
    'website': artist.website,
    'image_link': artist.image_link,
    'facebook_link': artist.facebook_link,
    'seeking_venue': artist.seeking_venue,
    'seeking_description': artist.seeking_description,
    'past_shows': past_shows,
    'upcoming_shows': upcoming_shows,
    'past_shows_count': len(past_shows),
    'upcoming_shows_count': len(upcoming_shows)
  }
  
  return render_template('pages/show_artist.html', artist=data)


#  ----------------------------------------------------------------
#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

  error = False
  try:
    artist = Artist.query.get(artist_id)
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.genres = request.form.getlist('genres')
    artist.facebook_link = request.form['facebook_link']
    artist.website = request.form['website']
    artist.image_link = request.form['image_link']

    if request.form['seeking_venue'] == 'True':
      artist.seeking_venue = True
    else:
      artist.seeking_venue = False
    artist.seeking_description = request.form['seeking_description']
    db.session.add(artist)
    db.session.commit()

  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())

  finally:
    db.session.close()

  if error:
    return  abort(500)
  else:
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = False
  try:
    venue = Venue.query.get(venue_id)
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.phone = request.form['phone']
    venue.address = request.form['address']
    venue.genres = request.form.getlist('genres')
    venue.facebook_link = request.form['facebook_link']
    venue.website = request.form['website']
    venue.image_link = request.form['image_link']

    if request.form['seeking_talent'] == 'True':
      venue.seeking_talent = True
    else:
      venue.seeking_talent = False
    venue.seeking_description = request.form['seeking_description']
    db.session.add(venue)
    db.session.commit()

  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())

  finally:
    db.session.close()

  if error:
    return  abort(500)
  else:
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  artist = Artist()
  error = False

  try:
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.genres = request.form.getlist('genres')
    artist.facebook_link = request.form['facebook_link']
    artist.website = request.form['website']
    artist.image_link = request.form['image_link']

    if request.form['seeking_venue'] == 'True':
      artist.seeking_venue = True
    else:
      artist.seeking_venue = False
    artist.seeking_description = request.form['seeking_description']

    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  if error:
    flash('An error occurred: Artist ' + request.form['name'] + ' could not be listed!')
    abort(500)
  else:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows = Show.query.join(Artist).join(Venue).all()

  data = []
  for show in shows:
    data.append({
      'venue_id': show.venues.id,
      'venue_name': show.venues.name,
      'artist_id': show.artists.id,
      'artist_name': show.artists.name,
      'artist_image_link': show.artists.image_link,
      'start_time': str(show.date)
    })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  show = Show()

  try:
    show.artist_id = request.form['artist_id']
    show.venue_id = request.form['venue_id']
    show.date = request.form['start_time']

    db.session.add(show)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  
  if error:
    flash('An error occurred. Show could not be listed.')
    abort(500)
  else:
    flash('Show was successfully listed!')
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
