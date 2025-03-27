import { useState } from "react";
import './App.css';

function App() {
  const [file1, setFile1] = useState(null);
  const [file2, setFile2] = useState(null);
  const [heightInches, setHeightInches] = useState(null); // Default 5'8" in inches
  const [message, setMessage] = useState("");
  const [measurements, setMeasurements] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!file1 || !file2) {
      setMessage("Please upload both images.");
      return;
    }

    setLoading(true);
    setMessage("Processing images...");

    const formData = new FormData();
    formData.append("front_image", file1);
    formData.append("side_image", file2);
    // Convert inches to cm for backend
    formData.append("height", (heightInches * 2.54).toString());

    try {
      const response = await fetch("http://localhost:5000/upload", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setMeasurements(data.measurements);
        setMessage("Measurements calculated successfully!");
      } else {
        const error = await response.json();
        setMessage(`Error: ${error.error || "Failed to process images"}`);
      }
    } catch (error) {
      setMessage("An error occurred. Please try again.");
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const getAssessmentColor = (assessment) => {
    switch (assessment) {
      case "above average":
        return "#4CAF50";  // Green
      case "below average":
        return "#f44336";  // Red
      default:
        return "#2196F3";  // Blue
    }
  };

  return (
    <div className="container">
      <h1>Body Measurements Scanner</h1>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Height (inches):</label>
          <input 
            type="number" 
            value={heightInches} 
            onChange={(e) => setHeightInches(parseFloat(e.target.value))}
            min="40"
            max="100"
            step="0.1"
          />
        </div>
        
        <div className="form-group">
          <label>Front View Image:</label>
          <input 
            type="file" 
            onChange={(e) => setFile1(e.target.files[0])}
            accept="image/*"
          />
        </div>
        
        <div className="form-group">
          <label>Side View Image:</label>
          <input 
            type="file" 
            onChange={(e) => setFile2(e.target.files[0])}
            accept="image/*"
          />
        </div>
        
        <button type="submit" disabled={loading}>
          {loading ? "Processing..." : "Calculate Measurements"}
        </button>
      </form>

      {message && <p className={message.includes("Error") ? "error-message" : "success-message"}>{message}</p>}

      {measurements && (
        <div className="measurements">
          <h2>Body Measurements</h2>
          <div className="measurements-grid">
            {Object.entries(measurements).map(([key, value]) => {
              // Convert cm to inches (1 cm = 0.393701 inches)
              const inches = (value * 0.393701).toFixed(1);
              return (
                <div key={key} className="measurement-card">
                  <h3>{key}</h3>
                  <div className="measurement-value">
                    <span className="value">{inches} inches</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;