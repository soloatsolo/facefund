import React, { useState, useEffect } from 'react';
import { getContacts, createContact, linkFaceToContact } from '../services/faceApi';
import { checkContactsPermission, requestContactsAccess, syncContacts } from '../utils/contactsSync';
import PermissionRequest from './PermissionRequest';

const Contacts = ({ selectedFace, onContactLinked }) => {
    const [contacts, setContacts] = useState([]);
    const [showForm, setShowForm] = useState(false);
    const [error, setError] = useState(null);
    const [showPermissionRequest, setShowPermissionRequest] = useState(true);
    const [hasPermission, setHasPermission] = useState(false);
    const [syncing, setSyncing] = useState(false);
    const [formData, setFormData] = useState({
        name: '',
        phone: '',
        email: '',
        address: '',
        birth_date: '',
        occupation: '',
        notes: ''
    });

    useEffect(() => {
        checkInitialPermission();
    }, []);

    const checkInitialPermission = async () => {
        const hasAccess = await checkContactsPermission();
        if (hasAccess) {
            setHasPermission(true);
            setShowPermissionRequest(false);
            await loadContacts();
        }
    };

    const loadContacts = async () => {
        try {
            const contactsList = await getContacts();
            setContacts(contactsList);
        } catch (err) {
            setError('Failed to load contacts');
        }
    };

    const handlePermissionAllow = async () => {
        try {
            const granted = await requestContactsAccess();
            if (granted) {
                setHasPermission(true);
                setShowPermissionRequest(false);
                await handleSync();
            } else {
                setError('Permission denied');
                setShowPermissionRequest(false);
            }
        } catch (err) {
            setError('Failed to request contacts permission');
            setShowPermissionRequest(false);
        }
    };

    const handlePermissionDeny = () => {
        setError('Contacts access is required for synchronization');
        setShowPermissionRequest(false);
    };

    const handleSync = async () => {
        setSyncing(true);
        try {
            const deviceContacts = await syncContacts();
            // Create new contacts from device contacts
            for (const contact of deviceContacts) {
                await createContact({
                    ...contact,
                    notes: 'Imported from device contacts'
                });
            }
            await loadContacts();
        } catch (err) {
            setError('Failed to sync contacts: ' + err.message);
        } finally {
            setSyncing(false);
        }
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await createContact(formData);
            setShowForm(false);
            setFormData({
                name: '',
                phone: '',
                email: '',
                address: '',
                birth_date: '',
                occupation: '',
                notes: ''
            });
            await loadContacts();
        } catch (err) {
            setError('Failed to create contact');
        }
    };

    const handleLinkContact = async (contactId) => {
        if (!selectedFace) return;
        try {
            await linkFaceToContact(selectedFace.id, contactId);
            if (onContactLinked) {
                onContactLinked(contactId);
            }
        } catch (err) {
            setError('Failed to link contact to face');
        }
    };

    if (showPermissionRequest) {
        return (
            <PermissionRequest 
                type="contacts"
                onAllow={handlePermissionAllow}
                onDeny={handlePermissionDeny}
            />
        );
    }

    return (
        <div className="contacts-section">
            <h2>Contacts</h2>
            {error && <div className="error-message">{error}</div>}
            
            <div className="contacts-controls">
                <button onClick={() => setShowForm(!showForm)}>
                    {showForm ? 'Cancel' : 'Add New Contact'}
                </button>
                {hasPermission && (
                    <button 
                        onClick={handleSync}
                        disabled={syncing}
                    >
                        {syncing ? 'Syncing...' : 'Sync Device Contacts'}
                    </button>
                )}
            </div>

            {showForm && (
                <form onSubmit={handleSubmit} className="contact-form">
                    <div>
                        <label>Name:</label>
                        <input
                            type="text"
                            name="name"
                            value={formData.name}
                            onChange={handleInputChange}
                            required
                        />
                    </div>
                    <div>
                        <label>Phone:</label>
                        <input
                            type="tel"
                            name="phone"
                            value={formData.phone}
                            onChange={handleInputChange}
                        />
                    </div>
                    <div>
                        <label>Email:</label>
                        <input
                            type="email"
                            name="email"
                            value={formData.email}
                            onChange={handleInputChange}
                        />
                    </div>
                    <div>
                        <label>Address:</label>
                        <input
                            type="text"
                            name="address"
                            value={formData.address}
                            onChange={handleInputChange}
                        />
                    </div>
                    <div>
                        <label>Birth Date:</label>
                        <input
                            type="date"
                            name="birth_date"
                            value={formData.birth_date}
                            onChange={handleInputChange}
                        />
                    </div>
                    <div>
                        <label>Occupation:</label>
                        <input
                            type="text"
                            name="occupation"
                            value={formData.occupation}
                            onChange={handleInputChange}
                        />
                    </div>
                    <div>
                        <label>Notes:</label>
                        <textarea
                            name="notes"
                            value={formData.notes}
                            onChange={handleInputChange}
                        />
                    </div>
                    <button type="submit">Save Contact</button>
                </form>
            )}

            <div className="contacts-list">
                {contacts.map(contact => (
                    <div key={contact.id} className="contact-card">
                        <h3>{contact.name}</h3>
                        {contact.phone && <p>📞 {contact.phone}</p>}
                        {contact.email && <p>✉️ {contact.email}</p>}
                        {contact.address && <p>🏠 {contact.address}</p>}
                        {contact.occupation && <p>💼 {contact.occupation}</p>}
                        {selectedFace && (
                            <button onClick={() => handleLinkContact(contact.id)}>
                                Link to Selected Face
                            </button>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
};

export default Contacts;