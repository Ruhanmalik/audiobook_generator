import axios from 'axios';
import { useState } from 'react';
import '../css/home.css';

function Home() {
    const [File, setFile] = useState(null);

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
    };

    const handleUpload = () => {
        if (!File) {
            alert('Please select a file first');
            return;
        }
        const formData = new FormData();
        formData.append('file', File);

        axios.post('/text', formData)
        .then(response => {
            console.log(response.data);
        })
        .catch(error => {
            console.error(error);
        });
    }
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
                        />
                    </label>
                    {File && (
                        <p className="file-name">{File.name}</p>
                    )}
                    <button onClick={handleUpload} className="upload-button">
                        Upload & Convert
                    </button>
                </div>
            </div>
        </div>
    );
}

export default Home;