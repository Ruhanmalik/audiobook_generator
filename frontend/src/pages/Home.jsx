import axios from 'axios';
import { useState } from 'react';

function Home() {
    const [File, setFile] = useState(null);

    const handleUpload = (e) => {
        const File = e.target.files[0]
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
        <div>
            <input type="file" accept=".epub" />
            <button onClick={handleUpload} href="/Text">Upload</button>
        </div>
    );
}

export default Home;