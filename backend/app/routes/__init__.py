from flask import Blueprint, request, jsonify, send_file
import os
import logging
from datetime import datetime
from app.services.face_detection import detect_faces
from app.services.file_storage import SecureFileStorage
from app.services.error_handler import ErrorHandler, FileProcessingError, ValidationError, PermissionError
from app.services.rate_limiter import rate_limit
from app.models import FaceEntry, Face, Contact, Photo, db
from functools import wraps

logger = logging.getLogger(__name__)
face_recognition_bp = Blueprint('face_recognition', __name__)

UPLOAD_FOLDER = 'app/static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Initialize secure file storage
file_storage = SecureFileStorage(UPLOAD_FOLDER, ALLOWED_EXTENSIONS)

def handle_errors(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {f.__name__}: {str(e)}")
            response, status_code = ErrorHandler.handle_error(e)
            return jsonify(response), status_code
    return decorated_function

@face_recognition_bp.route('/api/detect-face', methods=['POST'])
@handle_errors
@rate_limit(calls=50, period=60)  # 50 calls per minute
def detect_face():
    if 'file' not in request.files:
        raise ValidationError('No file provided', 'file')
    
    file = request.files['file']
    if file.filename == '':
        raise ValidationError('No file selected', 'file')
    
    logger.info(f"Processing face detection for file: {file.filename}")
    
    # Save file securely
    filename, filepath = file_storage.save_file(file, file.filename)
    if not filename:
        raise FileProcessingError('Invalid file format', file.filename)
    
    try:
        # Process the image for face detection
        detection_results = detect_faces(filepath)
        logger.info(f"Detected {len(detection_results['faces'])} faces in {filename}")
        
        # Store each detected face in the database
        stored_faces = []
        for face in detection_results['faces']:
            face_entry = FaceEntry(
                image_path=filepath,
                face_location=face['location']
            )
            db.session.add(face_entry)
            stored_faces.append(face_entry.to_dict())
        
        # Create a photo entry
        photo = Photo(
            filename=filename,
            filepath=filepath,
            metadata={
                'detection_date': datetime.utcnow().isoformat(),
                'faces_detected': len(detection_results['faces'])
            }
        )
        db.session.add(photo)
        db.session.commit()
        
        # Include the stored face IDs and photo ID in the response
        detection_results['stored_faces'] = stored_faces
        detection_results['photo_id'] = photo.id
        
        return jsonify(detection_results)
    except Exception as e:
        logger.error(f"Error processing {filename}: {str(e)}")
        db.session.rollback()
        if os.path.exists(filepath):
            file_storage.delete_file(filename)
        raise

@face_recognition_bp.route('/api/photos/scan', methods=['POST'])
@handle_errors
@rate_limit(calls=10, period=300)  # 10 calls per 5 minutes
def scan_photos():
    data = request.json
    directory = data.get('directory', UPLOAD_FOLDER)
    
    if not os.path.exists(directory):
        raise ValidationError('Directory does not exist', 'directory')
    
    if not os.access(directory, os.R_OK):
        raise PermissionError('No read access to directory', directory)
    
    logger.info(f"Starting batch scan of directory: {directory}")
    results = []
    errors = []
    
    for filename in os.listdir(directory):
        if any(filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS):
            filepath = os.path.join(directory, filename)
            try:
                # Process image for face detection
                detection_result = detect_faces(filepath)
                logger.info(f"Processed {filename}: found {len(detection_result['faces'])} faces")
                
                # Create Photo entry
                photo = Photo(
                    filename=filename,
                    filepath=filepath,
                    metadata={
                        'scan_date': datetime.utcnow().isoformat(),
                        'faces_detected': len(detection_result['faces'])
                    }
                )
                db.session.add(photo)
                
                results.append({
                    'filename': filename,
                    'faces_detected': len(detection_result['faces'])
                })
            except Exception as e:
                logger.error(f"Error processing {filename}: {str(e)}")
                errors.append({
                    'filename': filename,
                    'error': str(e)
                })
                continue
    
    if results:
        db.session.commit()
        logger.info(f"Batch scan completed. Processed {len(results)} files, {len(errors)} errors")
    
    return jsonify({
        'results': results,
        'errors': errors,
        'total_processed': len(results),
        'total_errors': len(errors)
    })

@face_recognition_bp.route('/api/photos/<int:photo_id>/link-face', methods=['POST'])
@handle_errors
def link_photo_to_face(photo_id):
    data = request.json
    if not data or 'face_id' not in data:
        raise ValidationError('face_id is required', 'face_id')
    
    face_id = data['face_id']
    photo = Photo.query.get_or_404(photo_id)
    face = Face.query.get_or_404(face_id)
    
    photo.face_id = face_id
    db.session.commit()
    
    return jsonify({'message': 'Photo linked to face successfully'})

@face_recognition_bp.route('/api/photos/organize', methods=['GET'])
@handle_errors
def get_organized_photos():
    # Get all photos with their associated faces and contacts
    photos = Photo.query.all()
    organized = {}
    
    for photo in photos:
        if photo.face_id:
            face = Face.query.get(photo.face_id)
            if face:
                key = f"face_{face.id}"
                name = f"Unknown Person {face.id}"
                
                if face.contact_id:
                    contact = Contact.query.get(face.contact_id)
                    if contact:
                        key = f"contact_{contact.id}"
                        name = contact.name
                
                if key not in organized:
                    organized[key] = {
                        'id': key,
                        'name': name,
                        'photos': []
                    }
                
                organized[key]['photos'].append({
                    'id': photo.id,
                    'filename': photo.filename,
                    'metadata': photo.metadata
                })
    
    return jsonify({'groups': list(organized.values())})

@face_recognition_bp.route('/api/photos/<filename>', methods=['GET'])
@handle_errors
def get_photo(filename):
    filepath = file_storage.get_file_path(filename)
    if not filepath:
        raise FileProcessingError('Photo not found', filename)
    
    if not os.path.exists(filepath):
        raise FileProcessingError('Photo file missing', filename)
    
    try:
        return send_file(filepath)
    except Exception as e:
        raise FileProcessingError('Failed to send photo', filename, {'error': str(e)})

# Contact management routes
@face_recognition_bp.route('/api/contacts', methods=['GET'])
@handle_errors
def list_contacts():
    contacts = Contact.query.all()
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'phone': c.phone,
        'email': c.email,
        'address': c.address,
        'birth_date': c.birth_date.isoformat() if c.birth_date else None,
        'occupation': c.occupation,
        'notes': c.notes
    } for c in contacts])

@face_recognition_bp.route('/api/contacts', methods=['POST'])
@handle_errors
def create_contact():
    data = request.json
    if not data or 'name' not in data:
        raise ValidationError('name is required', 'name')
    
    try:
        contact = Contact(
            name=data['name'],
            phone=data.get('phone'),
            email=data.get('email'),
            address=data.get('address'),
            birth_date=datetime.strptime(data['birth_date'], '%Y-%m-%d').date() if data.get('birth_date') else None,
            occupation=data.get('occupation'),
            notes=data.get('notes')
        )
        db.session.add(contact)
        db.session.commit()
        
        return jsonify({
            'id': contact.id,
            'message': 'Contact created successfully'
        })
    except Exception as e:
        db.session.rollback()
        raise ValidationError('Failed to create contact', 'contact', {'error': str(e)})

@face_recognition_bp.route('/api/faces/<int:face_id>/link-contact', methods=['POST'])
@handle_errors
def link_face_to_contact(face_id):
    data = request.json
    if not data or 'contact_id' not in data:
        raise ValidationError('contact_id is required', 'contact_id')
    
    contact_id = data['contact_id']
    face = Face.query.get_or_404(face_id)
    contact = Contact.query.get_or_404(contact_id)
    
    face.contact_id = contact_id
    db.session.commit()
    
    return jsonify({'message': 'Face linked to contact successfully'})