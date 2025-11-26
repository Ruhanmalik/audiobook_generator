
function Input() {
  const handleUpload = () => {
    console.log('Upload clicked');
  };

  return (
    <div>
      <input type="file" accept=".epub" />
      <button onClick={handleUpload}>Upload</button>
    </div>
  );
}

export default Input;