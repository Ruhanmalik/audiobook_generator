import axios from 'axios';
import { useState } from 'react';
import '../css/home.css';

const StepIndicator = ({ currentStep, totalSteps = 3 }) => {
    const stepLabels = ['Upload EPUB', 'Review Text', 'Convert Audio'];

    return (
        <div className="step-indicator">
            <div className="step-track">
                {[...Array(totalSteps)].map((_, index) => {
                    const stepNumber = index + 1;
                    const isActive = stepNumber === currentStep;
                    const isCompleted = stepNumber < currentStep;

                    return (
                        <div key={stepNumber} className="step-item">
                            {stepNumber > 1 && (
                                <div className={`step-line ${isCompleted ? 'step-line-completed' : ''}`} />
                            )}
                            <div
                                className={[
                                    'step-circle',
                                    isActive && 'step-active',
                                    isCompleted && 'step-completed',
                                ]
                                    .filter(Boolean)
                                    .join(' ')}
                            >
                                {isCompleted ? (
                                    <svg className="step-check" viewBox="0 0 20 20">
                                        <path d="M5 10.5l3 3 7-7" fill="none" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                    </svg>
                                ) : (
                                    stepNumber
                                )}
                            </div>
                            <div className="step-label-wrapper">
                                {isCompleted && <span className="step-status">Completed</span>}
                                <div className="step-label">{stepLabels[index]}</div>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

function Home() {
    const CONST_BASE_URL = 'http://localhost:8000';

    const [currentStep, setCurrentStep] = useState(1);
    const [file, setFile] = useState(null);
    const [textContent, setTextContent] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [conversionProgress, setConversionProgress] = useState(0);
    const [taskId, setTaskId] = useState(null);
    const [outputFilename, setOutputFilename] = useState(null);
    const [progressMessage, setProgressMessage] = useState('');

    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        if (selectedFile && selectedFile.name.toLowerCase().endsWith('.epub')) {
            setFile(selectedFile);
            setError(null);
        } else {
            setError('Please select a valid EPUB file');
            setFile(null);
        }
    };

    const handleExtract = async () => {
        if (!file) {
            alert('Please select a file first');
            return;
        }
        setLoading(true);
        setError(null);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await axios.post(`${CONST_BASE_URL}/extract`, formData);
            setTextContent(response.data.text || response.data.content || '');
            setCurrentStep(2);
        } catch (err) {
            console.error(err);
            setError(err.response?.data?.detail || err.response?.data?.message || 'Extraction failed');
        } finally {
            setLoading(false);
        }
    };

    const handleTextChange = (e) => {
        setTextContent(e.target.value);
    };

    const handleDownloadText = () => {
        if (!textContent) return;
        const blob = new Blob([textContent], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `${(file?.name || 'audiobook').replace(/\.epub$/i, '')}.txt`;
        link.click();
        URL.revokeObjectURL(url);
    };

    const handleConvert = async () => {
        setLoading(true);
        setError(null);
        setConversionProgress(0);
        setProgressMessage('Starting conversion...');
        setCurrentStep(3);
        setOutputFilename(null);

        try {
            const response = await axios.post(`${CONST_BASE_URL}/convert`, {
                text: textContent,
                filename: file?.name,
            });
            
            const newTaskId = response.data.task_id;
            setTaskId(newTaskId);
            
            // Start polling for progress
            pollProgress(newTaskId);
        } catch (err) {
            console.error(err);
            setError(err.response?.data?.detail || err.response?.data?.message || 'Conversion failed');
            setLoading(false);
        }
    };

    const pollProgress = async (taskId) => {
        const pollInterval = setInterval(async () => {
            try {
                const response = await axios.get(`${CONST_BASE_URL}/progress/${taskId}`);
                const progressData = response.data;
                
                setConversionProgress(progressData.progress || 0);
                setProgressMessage(progressData.message || 'Processing...');
                
                if (progressData.status === 'completed') {
                    clearInterval(pollInterval);
                    setLoading(false);
                    setOutputFilename(progressData.output_file);
                    setProgressMessage('Conversion complete!');
                } else if (progressData.status === 'failed') {
                    clearInterval(pollInterval);
                    setLoading(false);
                    setError(progressData.error || 'Conversion failed');
                }
            } catch (err) {
                console.error('Error polling progress:', err);
                // Don't clear interval on error, keep trying
            }
        }, 1000); // Poll every second
    };

    const handleDownload = () => {
        if (!outputFilename) return;
        window.open(`${CONST_BASE_URL}/download/${outputFilename}`, '_blank');
    };

    const handleOpenFileLocation = async () => {
        if (!outputFilename) return;
        // Use Electron API if available, otherwise fallback to download
        if (window.electron && window.electron.showItemInFolder) {
            try {
                const result = await window.electron.showItemInFolder(`output/${outputFilename}`);
                if (!result.success) {
                    console.error('Failed to open file location:', result.error);
                    // Fallback to download
                    handleDownload();
                }
            } catch (err) {
                console.error('Error opening file location:', err);
                // Fallback to download
                handleDownload();
            }
        } else {
            // Fallback to download if Electron API not available
            handleDownload();
        }
    };

    const goBack = () => {
        if (currentStep > 1) {
            setCurrentStep(currentStep - 1);
            setError(null);
        }
    };

    const resetProcess = () => {
        setCurrentStep(1);
        setFile(null);
        setTextContent('');
        setConversionProgress(0);
        setError(null);
        setLoading(false);
        setTaskId(null);
        setOutputFilename(null);
        setProgressMessage('');
    };

    return (
        <div className="home-container">
            <StepIndicator currentStep={currentStep} />

            <div className="home-content">
                <h1 className="home-title">Epub Audiobook Generator</h1>

                {currentStep === 1 && (
                    <section className="card">
                        <p className="card-subtitle">Upload your EPUB file to get started</p>
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
                        {file && <p className="file-name">📄 {file.name}</p>}
                        {error && <p className="error-message">{error}</p>}
                        <button onClick={handleExtract} className="primary-button" disabled={loading || !file}>
                            {loading ? 'Extracting…' : 'Extract Text'}
                        </button>
                    </section>
                )}

                {currentStep === 2 && (
                    <section className="card">
                        <p className="card-subtitle">Review and edit the extracted text</p>
                        <textarea
                            value={textContent}
                            onChange={handleTextChange}
                            className="text-editor"
                            placeholder="Extracted text will appear here..."
                        />
                        {error && <p className="error-message">{error}</p>}
                        <div className="button-row">
                            <button onClick={goBack} className="ghost-button">
                                Back
                            </button>
                            <button onClick={handleDownloadText} className="secondary-button" disabled={!textContent}>
                                Download .txt
                            </button>
                            <button
                                onClick={handleConvert}
                                className="primary-button"
                                disabled={loading || !textContent}
                            >
                                Continue to Convert
                            </button>
                        </div>
                    </section>
                )}

                {currentStep === 3 && (
                    <section className="card">
                        <p className="card-subtitle">Converting your text to audiobook</p>
                        <div className="progress-wrapper">
                            <div className="progress-bar">
                                <div className="progress-indicator" style={{ width: `${conversionProgress}%` }}>
                                    {conversionProgress >= 12 && `${conversionProgress}%`}
                                </div>
                            </div>
                            {progressMessage && (
                                <p className="progress-hint">{progressMessage}</p>
                            )}
                            {loading && conversionProgress < 100 && (
                                <p className="progress-hint">Converting… Please wait</p>
                            )}
                            {conversionProgress === 100 && !loading && (
                                <p className="success-message">Conversion complete! ✓</p>
                            )}
                        </div>
                        {error && <p className="error-message">{error}</p>}
                        <div className="button-row">
                            {conversionProgress === 100 && !loading ? (
                                <>
                                    <button onClick={handleDownload} className="secondary-button">
                                        Download Audio
                                    </button>
                                    <button onClick={handleOpenFileLocation} className="secondary-button">
                                        Open File Location
                                    </button>
                                    <button onClick={resetProcess} className="primary-button">
                                        Convert Another File
                                    </button>
                                </>
                            ) : (
                                <button onClick={goBack} className="ghost-button" disabled={loading}>
                                    Back to Edit
                                </button>
                            )}
                        </div>
                    </section>
                )}
            </div>
        </div>
    );
}

export default Home;