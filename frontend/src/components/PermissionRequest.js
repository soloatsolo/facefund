import React from 'react';

const PermissionRequest = ({ type, onAllow, onDeny }) => {
    const messages = {
        camera: {
            title: 'Camera Access Required',
            description: 'We need access to your camera to detect faces in real-time. Your privacy is important to us - photos are only processed locally.'
        },
        storage: {
            title: 'Storage Access Required',
            description: 'We need access to your photo gallery to scan for faces. Your photos will remain private and are only processed locally.'
        },
        contacts: {
            title: 'Contacts Access Required',
            description: 'We need access to your contacts to link faces with your contact list. Your contacts information will remain private and secure.'
        }
    };

    const message = messages[type] || {
        title: 'Permission Required',
        description: 'This feature requires additional permissions to work.'
    };

    return (
        <div className="permission-request">
            <h3>{message.title}</h3>
            <p>{message.description}</p>
            <div className="permission-buttons">
                <button className="allow" onClick={onAllow}>Allow</button>
                <button className="deny" onClick={onDeny}>Deny</button>
            </div>
        </div>
    );
};

export default PermissionRequest;