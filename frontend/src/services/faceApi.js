import axios from 'axios';
import config from '../config';

const API_URL = config.API_URL;

export const detectFace = async (imageFile) => {
    const formData = new FormData();
    formData.append('file', imageFile);

    try {
        const response = await axios.post(`${API_URL}/detect-face`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    } catch (error) {
        throw error.response?.data || error.message;
    }
};

export const getFaceHistory = async () => {
    try {
        const response = await axios.get(`${API_URL}/faces`);
        return response.data;
    } catch (error) {
        throw error.response?.data || error.message;
    }
};

export const getContacts = async () => {
    try {
        const response = await axios.get(`${API_URL}/contacts`);
        return response.data;
    } catch (error) {
        throw error.response?.data || error.message;
    }
};

export const createContact = async (contactData) => {
    try {
        const response = await axios.post(`${API_URL}/contacts`, contactData);
        return response.data;
    } catch (error) {
        throw error.response?.data || error.message;
    }
};

export const linkFaceToContact = async (faceId, contactId) => {
    try {
        const response = await axios.post(`${API_URL}/faces/${faceId}/link-contact`, {
            contact_id: contactId
        });
        return response.data;
    } catch (error) {
        throw error.response?.data || error.message;
    }
};

export const scanPhotos = async (directory) => {
    try {
        const response = await axios.post(`${API_URL}/photos/scan`, { directory });
        return response.data;
    } catch (error) {
        throw error.response?.data || error.message;
    }
};

export const linkPhotoToFace = async (photoId, faceId) => {
    try {
        const response = await axios.post(`${API_URL}/photos/${photoId}/link-face`, {
            face_id: faceId
        });
        return response.data;
    } catch (error) {
        throw error.response?.data || error.message;
    }
};

export const getOrganizedPhotos = async () => {
    try {
        const response = await axios.get(`${API_URL}/photos/organize`);
        return response.data;
    } catch (error) {
        throw error.response?.data || error.message;
    }
};

export const getPhoto = async (filename) => {
    try {
        const response = await axios.get(`${API_URL}/photos/${filename}`, {
            responseType: 'blob'
        });
        return URL.createObjectURL(response.data);
    } catch (error) {
        throw error.response?.data || error.message;
    }
};