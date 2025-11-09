import axios from 'axios';
import { useState } from 'react';
import '../css/home.css';

function Home() {

    const CONST_BASE_URL = 'http://localhost:8000';

    const [file, setFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(false);

    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        if (selectedFile && selectedFile.name.endsWith('.epub')) {
            setFile(selectedFile);
            setError(null);
        } else {
            setError('Please select a valid EPUB file');
            setFile(null);
        }
    };

    const handleUpload = async () => {
        if (!file) {
            alert('Please select a file first');
            return;
        }
        setLoading(true);
        setError(null);
        setSuccess(false);

        const formData = new FormData();
        formData.append('file', file);

        
        try {
            const response = await axios.post(`${CONST_BASE_URL}/text`, formData);
            console.log(response.data);
            setSuccess(true);
        } catch (error) {
            console.error(error);
            setError(error.response?.data?.detail || error.response?.data?.message || 'Upload failed');
        } finally {
            setLoading(false);
        }
    };
    return (
        <div className="home-container">
            <div className="home-content">
                <h1 className="home-title">Epub Audiobook Generator</h1>
                <p className="home-subtitle">Upload your EPUB file to convert it to an audiobook</p>
                <div className="upload-section">
                    <label htmlFor="file-input" className="file-label">
                        <span className="file-label-text">Choose EPUB File</span>
                        <input 
                            id="file-input"
                            type="file" 
                            accept=".epub" 
                            onChange={handleFileChange}
                            className="file-input"
                            disabled={loading}
                        />
                    </label>
                    {file && (
                        <p className="file-name">{file.name}</p>
                    )}
                    {error && <p className="error-message">{error}</p>}
                    {success && <p className="success-message">Conversion started successfully!</p>}
                    <button 
                        onClick={handleUpload} 
                        className="upload-button"
                        disabled={loading || !file}
                    >
                        {loading ? 'Converting...' : 'Upload & Convert'}
                    </button>
                </div>
            </div>
        </div>
    );
}

export default Home;