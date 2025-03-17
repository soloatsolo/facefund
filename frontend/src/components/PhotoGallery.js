import React, { useState, useEffect } from 'react';
import { scanPhotos, getOrganizedPhotos, getPhoto } from '../services/faceApi';
import PermissionRequest from './PermissionRequest';

const PhotoGallery = ({ onFaceSelected }) => {
    const [scanning, setScanning] = useState(false);
    const [photos, setPhotos] = useState([]);
    const [error, setError] = useState(null);
    const [showPermissionRequest, setShowPermissionRequest] = useState(true);
    const [hasPermission, setHasPermission] = useState(false);
    const [selectedDirectory, setSelectedDirectory] = useState('');
    const [currentView, setCurrentView] = useState('grid');
    const [organizing, setOrganizing] = useState(false);
    const [organizedGroups, setOrganizedGroups] = useState([]);
    const [photoUrls, setPhotoUrls] = useState({});

    useEffect(() => {
        if (currentView === 'faces' && organizedGroups.length === 0) {
            loadOrganizedPhotos();
        }
    }, [currentView]);

    const loadOrganizedPhotos = async () => {
        setOrganizing(true);
        try {
            const { groups } = await getOrganizedPhotos();
            setOrganizedGroups(groups);

            // Load photo URLs for all photos in groups
            const urls = {};
            for (const group of groups) {
                for (const photo of group.photos) {
                    if (!urls[photo.filename]) {
                        urls[photo.filename] = await getPhoto(photo.filename);
                    }
                }
            }
            setPhotoUrls(urls);
        } catch (err) {
            setError('Failed to organize photos: ' + err.message);
        } finally {
            setOrganizing(false);
        }
    };

    const handlePermissionAllow = () => {
        setHasPermission(true);
        setShowPermissionRequest(false);
    };

    const handlePermissionDeny = () => {
        setError('Storage access is required to manage photos');
        setShowPermissionRequest(false);
    };

    const handleDirectoryChange = (e) => {
        setSelectedDirectory(e.target.value);
    };

    const handleScan = async () => {
        if (!selectedDirectory) {
            setError('Please select a directory to scan');
            return;
        }

        setScanning(true);
        setError(null);
        try {
            const results = await scanPhotos(selectedDirectory);
            setPhotos(prev => [...prev, ...results.results]);
            
            // Load photo URLs for new photos
            const newUrls = {};
            for (const photo of results.results) {
                if (!photoUrls[photo.filename]) {
                    newUrls[photo.filename] = await getPhoto(photo.filename);
                }
            }
            setPhotoUrls(prev => ({ ...prev, ...newUrls }));
        } catch (err) {
            setError('Failed to scan photos: ' + err.message);
        } finally {
            setScanning(false);
        }
    };

    const handlePhotoSelect = (photo) => {
        if (photo.faces && photo.faces.length > 0) {
            onFaceSelected(photo.faces[0]);
        }
    };

    const handleViewChange = (view) => {
        setCurrentView(view);
        if (view === 'faces' && organizedGroups.length === 0) {
            loadOrganizedPhotos();
        }
    };

    const renderGridView = () => (
        <div className="photo-grid">
            {photos.map((photo, index) => (
                <div 
                    key={index} 
                    className="photo-item"
                    onClick={() => handlePhotoSelect(photo)}
                >
                    <img 
                        src={photoUrls[photo.filename] || 'placeholder.jpg'}
                        alt={`Photo ${photo.filename}`}
                        onError={(e) => {
                            e.target.src = 'placeholder.jpg';
                            e.target.alt = 'Photo not available';
                        }}
                    />
                    <div className="photo-info">
                        <p>{photo.filename}</p>
                        {photo.faces && (
                            <p>Faces detected: {photo.faces.length}</p>
                        )}
                    </div>
                </div>
            ))}
        </div>
    );

    const renderFacesView = () => (
        <div className="faces-view">
            {organizedGroups.map(group => (
                <div key={group.id} className="face-group">
                    <div className="face-group-header">
                        <h3>{group.name}</h3>
                        <p>{group.photos.length} photos</p>
                    </div>
                    <div className="face-group-photos">
                        {group.photos.map((photo, index) => (
                            <div 
                                key={`${group.id}_${index}`}
                                className="face-group-photo"
                                onClick={() => handlePhotoSelect(photo)}
                            >
                                <img 
                                    src={photoUrls[photo.filename] || 'placeholder.jpg'}
                                    alt={`Photo in ${group.name}`}
                                    onError={(e) => {
                                        e.target.src = 'placeholder.jpg';
                                        e.target.alt = 'Photo not available';
                                    }}
                                />
                                <div className="photo-overlay">
                                    {photo.filename}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            ))}
        </div>
    );

    if (showPermissionRequest) {
        return (
            <PermissionRequest 
                type="storage"
                onAllow={handlePermissionAllow}
                onDeny={handlePermissionDeny}
            />
        );
    }

    return (
        <div className="photo-gallery">
            <h2>Photo Gallery</h2>
            {error && <div className="error-message">{error}</div>}

            <div className="gallery-controls">
                <div className="scan-controls">
                    <input
                        type="text"
                        value={selectedDirectory}
                        onChange={handleDirectoryChange}
                        placeholder="Enter directory path to scan"
                    />
                    <button 
                        onClick={handleScan}
                        disabled={scanning || !hasPermission}
                    >
                        {scanning ? 'Scanning...' : 'Scan Directory'}
                    </button>
                </div>

                <div className="view-controls">
                    <button
                        className={currentView === 'grid' ? 'active' : ''}
                        onClick={() => handleViewChange('grid')}
                    >
                        Grid View
                    </button>
                    <button
                        className={currentView === 'faces' ? 'active' : ''}
                        onClick={() => handleViewChange('faces')}
                        disabled={organizing || photos.length === 0}
                    >
                        {organizing ? 'Organizing...' : 'Organize by Faces'}
                    </button>
                </div>

                <input
                    type="file"
                    multiple
                    accept="image/*"
                    onChange={async (e) => {
                        const files = Array.from(e.target.files);
                        setScanning(true);
                        try {
                            for (const file of files) {
                                const formData = new FormData();
                                formData.append('file', file);
                                await scanPhotos(formData);
                            }
                            await loadOrganizedPhotos();
                        } catch (err) {
                            setError('Failed to process photos: ' + err.message);
                        } finally {
                            setScanning(false);
                        }
                    }}
                    style={{ display: 'none' }}
                    id="photo-upload"
                />
                <label htmlFor="photo-upload" className="button">
                    Upload Photos
                </label>
            </div>

            {organizing ? (
                <div className="organize-loader">
                    Organizing photos by faces...
                </div>
            ) : currentView === 'grid' ? (
                renderGridView()
            ) : (
                renderFacesView()
            )}
        </div>
    );
};

export default PhotoGallery;