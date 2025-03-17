import React, { useRef, useState, useCallback } from 'react';
import Webcam from 'react-webcam';
import PermissionRequest from './PermissionRequest';

const Camera = ({ onCapture }) => {
    const webcamRef = useRef(null);
    const [error, setError] = useState(null);
    const [showPermissionRequest, setShowPermissionRequest] = useState(true);
    const [hasPermission, setHasPermission] = useState(false);

    const handlePermissionAllow = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            stream.getTracks().forEach(track => track.stop()); // Stop the stream immediately
            setHasPermission(true);
            setShowPermissionRequest(false);
        } catch (err) {
            setError('Failed to access camera: ' + err.message);
            setShowPermissionRequest(false);
        }
    };

    const handlePermissionDeny = () => {
        setError('Camera access is required for this feature');
        setShowPermissionRequest(false);
    };

    const capture = useCallback(() => {
        const imageSrc = webcamRef.current?.getScreenshot();
        if (imageSrc) {
            // Convert base64 to blob
            fetch(imageSrc)
                .then(res => res.blob())
                .then(blob => {
                    const file = new File([blob], "capture.jpg", { type: "image/jpeg" });
                    onCapture(file);
                })
                .catch(err => setError('Failed to process image'));
        }
    }, [onCapture]);

    const videoConstraints = {
        width: 720,
        height: 480,
        facingMode: "user"
    };

    if (showPermissionRequest) {
        return (
            <PermissionRequest 
                type="camera"
                onAllow={handlePermissionAllow}
                onDeny={handlePermissionDeny}
            />
        );
    }

    if (error) {
        return <div className="error-message">{error}</div>;
    }

    return (
        <div className="camera-container">
            {hasPermission && (
                <>
                    <Webcam
                        audio={false}
                        ref={webcamRef}
                        screenshotFormat="image/jpeg"
                        videoConstraints={videoConstraints}
                        onUserMediaError={(err) => setError('Failed to access camera: ' + err.message)}
                    />
                    <button onClick={capture}>Capture Photo</button>
                </>
            )}
        </div>
    );
};

export default Camera;