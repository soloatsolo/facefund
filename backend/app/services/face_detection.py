import cv2
import numpy as np
from typing import Dict, List, Any
from PIL import Image
import os
from cryptography.fernet import Fernet
import base64
import json

# Initialize encryption key - in production, this should be stored securely
ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY', Fernet.generate_key())
cipher_suite = Fernet(ENCRYPTION_KEY)

def encrypt_data(data: dict) -> str:
    """Encrypt sensitive data"""
    json_data = json.dumps(data)
    encrypted_data = cipher_suite.encrypt(json_data.encode())
    return base64.b64encode(encrypted_data).decode()

def decrypt_data(encrypted_data: str) -> dict:
    """Decrypt sensitive data"""
    try:
        encrypted_bytes = base64.b64decode(encrypted_data.encode())
        decrypted_data = cipher_suite.decrypt(encrypted_bytes)
        return json.loads(decrypted_data)
    except Exception as e:
        print(f"Error decrypting data: {e}")
        return {}

def detect_faces(image_path: str) -> Dict[str, Any]:
    """
    Detect faces in an image using OpenCV's cascade classifier
    """
    # Load the pre-trained face detection classifier
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    # Read the image
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Failed to load image")
    
    # Convert to grayscale for face detection
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Detect faces
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30)
    )
    
    # Process results
    face_list = []
    for (x, y, w, h) in faces:
        face_location = {
            "left": int(x),
            "top": int(y),
            "right": int(x + w),
            "bottom": int(y + h)
        }
        
        # Extract the face region for feature extraction
        face_roi = gray[y:y+h, x:x+w]
        
        # Basic feature extraction (you might want to use a more sophisticated method)
        face_features = cv2.resize(face_roi, (64, 64)).flatten().tolist()
        
        face_dict = {
            "location": face_location,
            "features": encrypt_data({"features": face_features})
        }
        face_list.append(face_dict)
    
    return {
        "num_faces": len(face_list),
        "faces": face_list
    }

def crop_face(image_path: str, face_location: dict) -> Image:
    """
    Crop a face from an image given its location
    """
    image = Image.open(image_path)
    top = face_location.get('top', 0)
    right = face_location.get('right', 0)
    bottom = face_location.get('bottom', 0)
    left = face_location.get('left', 0)
    face_image = image.crop((left, top, right, bottom))
    return face_image

def compare_faces(face1_features: str, face2_features: str, threshold: float = 0.6) -> bool:
    """
    Compare two face feature sets and determine if they match
    """
    try:
        # Decrypt the encrypted feature data
        features1 = decrypt_data(face1_features)["features"]
        features2 = decrypt_data(face2_features)["features"]
        
        # Convert to numpy arrays for comparison
        features1 = np.array(features1)
        features2 = np.array(features2)
        
        # Calculate similarity (using cosine similarity)
        similarity = np.dot(features1, features2) / (np.linalg.norm(features1) * np.linalg.norm(features2))
        
        return similarity > threshold
    except Exception as e:
        print(f"Error comparing faces: {e}")
        return False