# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import dateutil.parser
import datetime
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort, jsonify
from flask_migrate import Migrate
import sys
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy.exc import SQLAlchemyError
from models import *
from forms import *

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

# index venues
@app.route('/venues')
def venues():
    venues_by_city = Venue.query.with_entities(Venue.city, Venue.state).distinct().all()
    places = []
    for city, state in venues_by_city:
        venues = Venue.query.filter_by(city=city, state=state).all()
        places.append({
            "city": city,
            "state": state,
            "venues": venues
        })
    return render_template('pages/venues.html', areas=places)


# search¬
@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term', '')
    return render_template('pages/search_venues.html',
                           venues=Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all(),
                           search_term=search_term)


# show venues
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.get(venue_id)
    if not venue:
        return render_template('errors/404.html')
    upcoming_shows = Show.query.filter(Show.venue_id == venue_id, Show.start_time > datetime.now())
    past_shows = Show.query.filter(Show.venue_id == venue_id, Show.start_time < datetime.now())
    return render_template('pages/show_venue.html',
                           venue=Venue.query.get(venue_id),
                           upcoming_shows=upcoming_shows.all(),
                           past_shows=past_shows.all(),
                           past_shows_count=past_shows.count(),
                           upcoming_shows_count=upcoming_shows.count(),
                           )


#  Create venue
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


# Post venues
@app.route('/venues/create', methods=['POST'])
def post_venue():
    form = VenueForm(request.form)
    venue = Venue()
    if form.validate():
        try:
            print('i am hit')
            venue.name = form.name.data
            venue.city = form.city.data
            venue.state = form.state.data
            venue.phone = form.phone.data
            venue.address = form.address.data
            venue.genres = form.genres.data
            venue.seeking_talent = form.seeking_talent.data
            venue.seeking_description = form.seeking_description.data
            venue.image_link = form.image_link.data
            venue.facebook_link = form.facebook_link.data
            db.session.add(venue)
            db.session.commit()
            flash('Venue ' + request.form['name'] + ' was successfully listed!')
        except Exception as e:
            db.session.rollback()
            print(f'Error ==> {e}')
            flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
        finally:
            db.session.close()
        return redirect(url_for('index'))
    else:
        print(form.phone.data)
        flash(form.errors)
        formErr = []
        for error in form.errors:
            formErr.append(form.errors[error])
        flash(formErr)
        return render_template('forms/new_venue.html', form=form)


# Edit venue

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    return render_template('forms/edit_venue.html', form=form, venue=venue)


# Update venue
@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def update_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    if form.validate():
        try:
            venue.name = form.name.data
            venue.city = form.city.data
            venue.state = form.state.data
            venue.address = form.address.data
            venue.phone = form.phone.data
            venue.genres = form.genres.data
            venue.facebook_link = form.facebook_link.data
            venue.website_link = form.website_link.data
            venue.image_link = form.image_link.data
            venue.seeking_talent = form.seeking_talent.data
            venue.seeking_description = form.seeking_description.data
            db.session.commit()
            flash('Venue ' + venue.name + ' has updated !')
        except Exception as e:
            db.session.rollback()
            print(f'Error ==> {e}')
            flash('An error occurred. Venue ' + venue.name + ' could not be listed.')
        finally:
            db.session.close()
        return redirect(url_for('show_venue', venue_id=venue_id))
    else:
        formErr = []
        for error in form.errors:
            formErr.append(form.errors[error])
        flash(form.errors)
        return render_template('forms/edit_venue.html', form=form, venue=venue)


#  Delete venue
@app.route('/venues/<venue_id>', methods=['POST'])
def delete_venue(venue_id):
    err = False
    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        flash('venue' + venue.name + 'was successfully deleted')
        db.session.commit()
    except:
        err = True
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('index'))


#  Artists
#  ----------------------------------------------------------------

# Index Artists
@app.route('/artists')
def artists():
    return render_template('pages/artists.html', artists=Artist.query.all())


# search Artist
@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term', '')
    return render_template('pages/search_venues.html',
                           venues=Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all(),
                           search_term=search_term)


# Show Artist
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    upcoming_shows = Show.query.filter(Show.artist_id == artist_id, Show.start_time > datetime.now())
    past_shows = Show.query.filter(Show.artist_id == artist_id, Show.start_time < datetime.now())
    return render_template('pages/show_artist.html',
                           artist=Artist.query.get(artist_id),
                           upcoming_shows=upcoming_shows.all(),
                           past_shows=past_shows.all(),
                           )


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def post_artist():
    err = False
    form = ArtistForm(request.form)
    artist = Artist()
    if form.validate():
        try:
            artist.name = form.name.data
            artist.city = form.city.data
            artist.state = form.state.data
            artist.phone = form.phone.data
            artist.genres = form.genres.data
            artist.facebook_link = form.facebook_link.data
            artist.image_link = form.facebook_link.data
            artist.seeking_talent = form.seeking_talent.data
            artist.seeking_description = form.name.data
            db.session.add(artist)
            db.session.commit()
            flash('Artist ' + request.form['name'] + ' was successfully listed!')
        except:
            err = True
            db.session.rollback()
            print(sys.exc_info())
            flash('An error occured. Artist ' + artist.name + ' Could not be listed!')
        finally:
            db.session.close()
        return redirect(url_for('index'))
    else:
        formErr = []
        for error in form.errors:
            formErr.append(form.errors[error])
        flash(form.errors)
        return render_template('forms/new_artist.html', form=form)


# Edit Artist
@app.route('/artists/<int:artist_id>/edit')
def edit_artist(artist_id):
    return render_template('forms/edit_artist.html', form=ArtistForm(), artist=Artist.query.get(artist_id))


# Update Artist
@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def update_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    if form.validate():
        try:
            artist.name = form.name.data
            artist.city = form.city.data
            artist.state = form.state.data
            artist.phone = form.phone.data
            artist.genres = form.genres.data
            artist.facebook_link = form.facebook_link.data
            artist.image_link = form.image_link.data
            artist.seeking_talent = form.seeking_talent.data
            artist.seeking_description = form.seeking_description.data
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f'Error ==> {e}')
            flash('An error occurred. Artist ' + artist.name + ' could not be listed.')
        finally:
            db.session.close()
        return redirect(url_for('show_artist', artist_id=artist_id))
    else:
        formErr = []
        for error in form.errors:
            formErr.append(form.errors[error])
        flash(form.errors)
        return render_template('forms/new_artist.html', form=form)


# Delete Artist
@app.route('/artists/<artist_id>', methods=['POST'])
def delete_artist(artist_id):
    err = False
    artist = Artist.query.get(artist_id)
    try:
        db.session.delete(artist)
        db.session.commit()
        flash('Artist ' + artist.name + 'was successfully deleted')
    except:
        err = True
        db.session.rollback()
        flash('Artist ' + artist.name + 'was NOT successfully deleted')
    finally:
        db.session.close()

    return redirect(url_for('index'))


@app.route('/shows')
def shows():
    return render_template('pages/shows.html', shows=Show.query.all())


@app.route('/shows/create')
def create_shows():
    return render_template('forms/new_show.html', form=ShowForm())


@app.route('/shows/create', methods=['POST'])
def post_show():
    err = False
    form = ShowForm(request.form)
    show = Show()
    try:
        show.venue_id = form.venue_id.data
        show.artist_id = form.artist_id.data
        show.start_time = form.start_time.data
        db.session.add(show)
        db.session.commit()
    except SQLAlchemyError as e:
        err = True
        db.session.rollback()
    finally:
        db.session.close()
    if err:
        flash('An error occurred. Show could not be listed.')
    else:
        flash('Show was successfully listed!')
    return redirect(url_for('index'))


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

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
