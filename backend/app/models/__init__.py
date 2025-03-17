from datetime import datetime
from .. import db

class FaceEntry(db.Model):
    """Model for storing face detection entries and search results"""
    id = db.Column(db.Integer, primary_key=True)
    image_path = db.Column(db.String(255), nullable=True, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    face_location = db.Column(db.JSON, nullable=False)
    search_results = db.Column(db.JSON, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'face_location': self.face_location,
            'search_results': self.search_results
        }

class Face(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True)
    encoding = db.Column(db.PickleType)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'), index=True)
    photos = db.relationship('Photo', backref='face', lazy=True)

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120), index=True)
    address = db.Column(db.String(200))
    birth_date = db.Column(db.Date)
    occupation = db.Column(db.String(100))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    faces = db.relationship('Face', backref='contact', lazy=True)

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False, index=True)
    filepath = db.Column(db.String(255), nullable=False)
    face_id = db.Column(db.Integer, db.ForeignKey('face.id'), index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    metadata = db.Column(db.JSON)