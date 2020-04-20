import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from src.database.models import db_drop_and_create_all, setup_db, Track, Playlist, Publication
from src.auth.auth import AuthError, requires_auth


app = Flask(__name__)
setup_db(app)
CORS(app)

# db_drop_and_create_all()

# ROUTES
@app.route('/')
def get_greeting():
    excited = 'true'
    greeting = "Hello" 
    if excited == 'true': greeting = greeting + "!!!!!"
    return greeting

# PLAYLIST --------------------------------------------------------
@app.route('/playlists', methods=['GET'])
def get_playlists():
    playlists = Playlist.query.all()

    playlists_short_form = []
    for playlist in playlists:
        playlist = playlist.short()
        playlists_short_form.append(playlist)

    return jsonify({
        "success": True,
        "playlists": playlists_short_form
    })   


@app.route('/playlists', methods=['POST'])
@requires_auth(permission='post:playlists')
def add_playlist(token):
    try:
        req = request.get_json()
        new_title = req.get('title', None)
        new_playlist = Playlist(title=new_title)
        if Playlist.query.filter(Playlist.title == new_title).one_or_none():
            abort(409)
        new_playlist.insert()
        print(new_playlist.long())
        return jsonify({
            'success': True,
            'playlists': [new_playlist.long()]
            })
    except Exception:
        abort(404)


@app.route('/playlists/<int:id>', methods=['PATCH'])
@requires_auth(permission='patch:playlists')
def update_playlist(token, id):
    req = request.get_json()
    title = req.get('title', None)

    if not title:
        abort(422)
    playlist = Playlist.query.filter(Playlist.id == id).one_or_none()

    if not playlist:
        abort(400)

    if title:
        playlist.title = title
    playlist.update()
    return jsonify({
        "success": True,
        "playlist": [playlist.long()]
    })

@app.route('/playlists/<int:id>', methods=['DELETE'])
@requires_auth(permission='delete:playlists')
def delete_playlist(token, id):
    try:
        playlist = Playlist.query.filter(Playlist.id == id).one_or_none()

        if not playlist:
            abort(400)

        playlist.delete()

        return jsonify({
            "success": True,
            "delete": id
        })
    except Exception:
        abort(422)


# TRACKS ---------------------------------------------------------
@app.route('/tracks', methods=['GET'])
@requires_auth(permission='get:tracks')
def get_tracks(token):
    tracks = Track.query.all()

    tracks_short_form = []
    for track in tracks:
        track = track.short()
        tracks_short_form.append(track)

    return jsonify({
        "success": True,
        "tracks": tracks_short_form
    })

@app.route('/tracks', methods=['POST'])
@requires_auth(permission='post:tracks')
def add_track(token):
    req = request.get_json()
    new_title = req.get('title', None)
    new_artist = req.get('artist', None)
    new_track = Track(title=new_title, artist=new_artist)
    if Track.query.filter(Track.title == new_title and
                            Track.artist == new_artist).one_or_none():
        abort(409)
    new_track.insert()
    return jsonify({
        'success': True,
        'tracks': [new_track.long()]
        })

@app.route('/tracks/<int:id>', methods=['PATCH'])
@requires_auth(permission='patch:tracks')
def update_track(token, id):
    req = request.get_json()
    title = req.get('title', None)
    artist = req.get('artist', None)

    if not title or not artist:
        abort(422)
    track = Track.query.filter(Track.id == id).one_or_none()

    if not track:
        abort(400)

    if title:
        track.title = title
    if artist:
        track.artist = artist
    track.update()
    return jsonify({
        "success": True,
        "tracks": [track.long()]
    })

@app.route('/tracks/<int:id>', methods=['DELETE'])
@requires_auth(permission='delete:tracks')
def remove_track(token, id):
    try:
        track = Track.query.filter(Track.id == id).one_or_none()

        if not track:
            abort(400)

        track.delete()

        return jsonify({
            "success": True,
            "delete": id
        })
    except Exception:
        abort(422)



# PUBLICATIONS --------------------------------------------------

@app.route('/playlists/<int:id>', methods=['GET'])
@requires_auth(permission='get:single-playlist')
def show_playlist(token, id):
    playlist = Playlist.query.filter(Playlist.id == id).one_or_none()
    if playlist:
        return jsonify({
            "success": True,
            "playlist": playlist.long()
        })
    else:
        abort(404)


@app.route('/playlists/<int:id>', methods=['POST'])
@requires_auth(permission='post:track-to-playlist')
def add_track_to_playlist(token, id):
    req = request.get_json()
    new_track_id = req.get('track_id', None)
    new_publication = Publication(track_id=new_track_id,
                                playlist_id=id)
    if Publication.query.filter(Publication.track_id == new_track_id).filter(Publication.playlist_id == id).all():
        abort(409)
    
    print(new_publication)
    new_publication.insert()
    
    return jsonify({
        'success': True,
        'track_id': new_publication.track_id,
        'playlist_id': new_publication.playlist_id
        })

@app.route('/playlists/<int:id>', methods=['DELETE'])
@requires_auth(permission='delete:track-from-playlist')
def remove_track_from_playlist(token, id):
    # ToDo
    raise NotImplementedError


# Error Handling ------------------------------------------------
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False,
                    "error": 422,
                    "message": "unprocessable"
                    }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404


@app.errorhandler(401)
def unprocessable(error):
    return jsonify({
                    "success": False,
                    "error": 401,
                    "message": "unprocessable"
                    }), 401

@app.errorhandler(409)
def resource_already_exists(error):
    return jsonify({
                    "success": False,
                    "error": 409,
                    "message": "resource_already_exists"
                    }), 409


if __name__ == '__main__':
    app.run()