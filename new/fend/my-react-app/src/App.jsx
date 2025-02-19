import { useState } from "react";
import './App.css';

function App() {
  const [file1, setFile1] = useState(null);
  const [file2, setFile2] = useState(null);
  const [message, setMessage] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!file1 || !file2) {
      setMessage("Please upload both images.");
      return;
    }

    const formData = new FormData();
    formData.append("front_image", file1);
    formData.append("side_image", file2);

    try {
      const response = await fetch("http://localhost:5000/upload", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "measurements.csv";
        document.body.appendChild(a);
        a.click();
        a.remove();
        setMessage("Measurements downloaded successfully!");
      } else {
        setMessage("Error uploading images.");
      }
      
    } catch (error) {
      setMessage("An error occurred. Please try again.");
      console.error(error);
    }
  };

  return (
    <div>
      <h1>Mannequin v -1</h1>
      <form onSubmit={handleSubmit}>
        <input type="file" onChange={(e) => setFile1(e.target.files[0])} />
        <input type="file" onChange={(e) => setFile2(e.target.files[0])} />
        <button type="submit">Upload</button>
      </form>
      <p>{message}</p>
    </div>
  );
}

export default App;