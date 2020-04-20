import os
import json

from sqlalchemy import Column, String, Integer, ForeignKey, Table
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

database_filename = "database.db"
project_dir = os.path.dirname(os.path.abspath(__file__))
database_path = "sqlite:///{}".format(os.path.join(project_dir, database_filename))

db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''
def setup_db(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)

def db_drop_and_create_all():
    db.drop_all()
    db.create_all()

'''
Track
A persistent song entity
'''
class Track(db.Model):  
    __tablename__ = 'Track'

    id = Column(Integer().with_variant(Integer, "sqlite"), primary_key=True)
    title = Column(String(120), unique=True)
    artist = Column(String(80), nullable=False)

    '''
    short()
        short form representation of the Drink model
    '''
    def short(self):
        if self.playlists:
            playlists = len(self.playlists)
        else:
            playlists = 0
        return {
            'id': self.id,
            'title': self.title,
            'artist': self.artist,
            'playlists': playlists
        }

    '''
    long()
        long form representation of the Track model
    '''
    def long(self):
        playlists_long_form = []
        if len(self.playlists) > 0:
            for publication in self.playlists:
                playlist = Playlist.query.filter(Playlist.id == publication.playlist_id).one_or_none()
                if playlist:
                    playlists_long_form.append({'title': playlist.title})
        return {
            'id': self.id,
            'title': self.title,
            'artist': self.artist,
            'playlists': playlists_long_form
        }

    '''
    insert()
        inserts a new model into a database
        the model must have a unique name
        the model must have a unique id or null id
        EXAMPLE
            drink = Drink(title=req_title, recipe=req_recipe)
            drink.insert()
    '''
    def insert(self):
        db.session.add(self)
        db.session.commit()

    '''
    delete()
        deletes a new model into a database
        the model must exist in the database
        EXAMPLE
            drink = Drink(title=req_title, recipe=req_recipe)
            drink.delete()
    '''
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    '''
    update()
        updates a new model into a database
        the model must exist in the database
        EXAMPLE
            drink = Drink.query.filter(Drink.id == id).one_or_none()
            drink.title = 'Black Coffee'
            drink.update()
    '''
    def update(self):
        db.session.commit()

    def __repr__(self):
        return json.dumps(self.short())



'''
Playlist
A persistent playlist entity
'''
class Playlist(db.Model):  
    __tablename__ = 'Playlist'

    id = Column(Integer().with_variant(Integer, "sqlite"), primary_key=True)
    title = Column(String(120), unique=True)

    '''
    short()
        short form representation of the Playlist model
    '''
    def short(self):
        if self.tracks:
            tracks = len(self.tracks)
        else:
            tracks = 0
        return {
            'id': self.id,
            'title': self.title,
            'tracks': tracks
        }

    '''
    long()
        long form representation of the Playlist model
    '''
    def long(self):
        tracks_long_form = []
        if len(self.tracks) > 0:
            for publication in self.tracks:
                track = Track.query.filter(Track.id == publication.track_id).one_or_none()
                if track:
                    tracks_long_form.append({'title': track.title, 'artist': track.artist})
        return {
            'id': self.id,
            'title': self.title,
            'tracks': tracks_long_form
        }

    '''
    insert()
        inserts a new model into a database
        the model must have a unique name
        the model must have a unique id or null id
        EXAMPLE
            drink = Drink(title=req_title, recipe=req_recipe)
            drink.insert()
    '''
    def insert(self):
        db.session.add(self)
        db.session.commit()

    '''
    delete()
        deletes a new model into a database
        the model must exist in the database
        EXAMPLE
            drink = Drink(title=req_title, recipe=req_recipe)
            drink.delete()
    '''
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    '''
    update()
        updates a new model into a database
        the model must exist in the database
        EXAMPLE
            drink = Drink.query.filter(Drink.id == id).one_or_none()
            drink.title = 'Black Coffee'
            drink.update()
    '''
    def update(self):
        db.session.commit()

    def __repr__(self):
        return json.dumps(self.short())


'''
Playlist
Model to associate tracks that are published to playlists
'''
class Publication(db.Model):
    __tablename__ = 'Publication'

    playlist_id = db.Column(db.Integer, db.ForeignKey('Playlist.id'), primary_key=True)
    track_id = db.Column(db.Integer, db.ForeignKey('Track.id'), primary_key=True)

    playlist = db.relationship('Playlist', backref=db.backref('tracks',
                                            cascade="save-update, merge, "
                                                "delete, delete-orphan"))
    track = db.relationship('Track', backref=db.backref('playlists',
                                    cascade="save-update, merge, "
                                                "delete, delete-orphan"))

    def insert(self):
        db.session.add(self)
        db.session.commit()

    '''
    delete()
        deletes a new model into a database
        the model must exist in the database
        EXAMPLE
            drink = Drink(title=req_title, recipe=req_recipe)
            drink.delete()
    '''
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    '''
    update()
        updates a new model into a database
        the model must exist in the database
        EXAMPLE
            drink = Drink.query.filter(Drink.id == id).one_or_none()
            drink.title = 'Black Coffee'
            drink.update()
    '''
    def update(self):
        db.session.commit()

    def __repr__(self):
        return f'<Publication - playlist_id: {self.playlist_id}, track_id:{self.track_id}>'