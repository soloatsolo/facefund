import React, { useState, useEffect } from 'react';
import Camera from './Camera';
import Contacts from './Contacts';
import PhotoGallery from './PhotoGallery';
import { detectFace, getFaceHistory } from '../services/faceApi';

const FaceDetection = () => {
    const [processing, setProcessing] = useState(false);
    const [results, setResults] = useState(null);
    const [error, setError] = useState(null);
    const [faceHistory, setFaceHistory] = useState([]);
    const [viewMode, setViewMode] = useState('capture'); // 'capture', 'history', 'contacts', or 'gallery'
    const [selectedFace, setSelectedFace] = useState(null);

    useEffect(() => {
        loadFaceHistory();
    }, []);

    const loadFaceHistory = async () => {
        try {
            const history = await getFaceHistory();
            setFaceHistory(history);
        } catch (err) {
            console.error('Failed to load face history:', err);
        }
    };

    const handleCapture = async (imageFile) => {
        setProcessing(true);
        setError(null);
        try {
            const detectionResults = await detectFace(imageFile);
            setResults(detectionResults);
            await loadFaceHistory();
        } catch (err) {
            setError(err.message || 'Failed to process image');
            setResults(null);
        } finally {
            setProcessing(false);
        }
    };

    const handleFileUpload = (event) => {
        const file = event.target.files[0];
        if (file) {
            handleCapture(file);
        }
    };

    const handleFaceSelect = (face) => {
        setSelectedFace(face);
        setViewMode('contacts'); // Switch to contacts view to link the face
    };

    const handleContactLinked = () => {
        setSelectedFace(null);
        loadFaceHistory();
    };

    return (
        <div className="face-detection">
            <h1>Face Detection App</h1>
            
            <div className="view-controls">
                <button 
                    className={viewMode === 'capture' ? 'active' : ''}
                    onClick={() => setViewMode('capture')}
                >
                    Capture
                </button>
                <button 
                    className={viewMode === 'history' ? 'active' : ''}
                    onClick={() => setViewMode('history')}
                >
                    History
                </button>
                <button 
                    className={viewMode === 'contacts' ? 'active' : ''}
                    onClick={() => setViewMode('contacts')}
                >
                    Contacts
                </button>
                <button 
                    className={viewMode === 'gallery' ? 'active' : ''}
                    onClick={() => setViewMode('gallery')}
                >
                    Photo Gallery
                </button>
            </div>

            {viewMode === 'capture' && (
                <div className="capture-section">
                    <Camera onCapture={handleCapture} />
                    <div className="upload-section">
                        <p>Or upload an image:</p>
                        <input
                            type="file"
                            accept="image/*"
                            onChange={handleFileUpload}
                        />
                    </div>

                    {processing && <div className="processing">Processing image...</div>}
                    
                    {error && (
                        <div className="error-message">
                            Error: {error}
                        </div>
                    )}

                    {results && (
                        <div className="results">
                            <h2>Detection Results</h2>
                            <p>Number of faces detected: {results.num_faces}</p>
                            {results.faces.map((face, index) => (
                                <div 
                                    key={index} 
                                    className="face-result"
                                    onClick={() => handleFaceSelect(face)}
                                >
                                    <h3>Face {index + 1}</h3>
                                    <p>Location:</p>
                                    <ul>
                                        <li>Top: {face.location.top}</li>
                                        <li>Right: {face.location.right}</li>
                                        <li>Bottom: {face.location.bottom}</li>
                                        <li>Left: {face.location.left}</li>
                                    </ul>
                                    <button onClick={() => handleFaceSelect(face)}>
                                        Link to Contact
                                    </button>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}

            {viewMode === 'history' && (
                <div className="history-section">
                    <h2>Detection History</h2>
                    {faceHistory.length === 0 ? (
                        <p>No previous detections found.</p>
                    ) : (
                        <div className="history-list">
                            {faceHistory.map((entry) => (
                                <div 
                                    key={entry.id} 
                                    className="history-entry"
                                    onClick={() => handleFaceSelect(entry)}
                                >
                                    <p>Detected on: {new Date(entry.timestamp).toLocaleString()}</p>
                                    <div className="face-location">
                                        <p>Face Location:</p>
                                        <ul>
                                            <li>Top: {entry.face_location.top}</li>
                                            <li>Right: {entry.face_location.right}</li>
                                            <li>Bottom: {entry.face_location.bottom}</li>
                                            <li>Left: {entry.face_location.left}</li>
                                        </ul>
                                    </div>
                                    {entry.search_results && (
                                        <div className="search-results">
                                            <p>Search Results:</p>
                                            <pre>{JSON.stringify(entry.search_results, null, 2)}</pre>
                                        </div>
                                    )}
                                    <button onClick={() => handleFaceSelect(entry)}>
                                        Link to Contact
                                    </button>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}

            {viewMode === 'contacts' && (
                <Contacts 
                    selectedFace={selectedFace}
                    onContactLinked={handleContactLinked}
                />
            )}

            {viewMode === 'gallery' && (
                <PhotoGallery 
                    onFaceSelected={handleFaceSelect}
                />
            )}
        </div>
    );
};

export default FaceDetection;