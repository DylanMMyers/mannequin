import { useState } from "react";
import './App.css';

function App() {
  const [front1, setFront1] = useState(null);
  const [front2, setFront2] = useState(null);
  const [side1, setSide1] = useState(null);
  const [side2, setSide2] = useState(null);
  const [heightInches, setHeightInches] = useState(null); // Default 5'8" in inches
  const [message, setMessage] = useState("");
  const [measurements, setMeasurements] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!front1 || !front2 || !side1 || !side2) {
      setMessage("Please upload all four images.");
      return;
    }

    setLoading(true);
    setMessage("Processing images...");

    const formData = new FormData();
    formData.append("front1", front1);
    formData.append("front2", front2);
    formData.append("side1", side1);
    formData.append("side2", side2);
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

  return (
    <div className="container">
      <h1>Mannequin</h1>
      
      <section className="upload-section">
        <h2>Upload Images</h2>
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
            <label>Front View 1 (elbows, knees, feet together):</label>
            <input 
              type="file" 
              onChange={(e) => setFront1(e.target.files[0])}
              accept="image/*"
            />
            <small>Stand with elbows, knees, and feet pressed together</small>
          </div>
          
          <div className="form-group">
            <label>Front View 2 (wrists on hips):</label>
            <input 
              type="file" 
              onChange={(e) => setFront2(e.target.files[0])}
              accept="image/*"
            />
            <small>Stand with wrists placed on the widest part of your hips</small>
          </div>

          <div className="form-group">
            <label>Side View 1 (chest measurement):</label>
            <input 
              type="file" 
              onChange={(e) => setSide1(e.target.files[0])}
              accept="image/*"
            />
            <small>Place hands at front and back of chest</small>
          </div>

          <div className="form-group">
            <label>Side View 2 (waist/hip measurement):</label>
            <input 
              type="file" 
              onChange={(e) => setSide2(e.target.files[0])}
              accept="image/*"
            />
            <small>Front hand at waist, back hand at back hip</small>
          </div>
          
          <button type="submit" disabled={loading}>
            {loading ? "Processing..." : "Calculate Measurements"}
          </button>
        </form>

        {message && <div className={`message ${message.includes("Error") ? "error-message" : "success-message"}`}>{message}</div>}
      </section>

      <section className="measurements-section">
        <h2>Body Measurements</h2>
        {measurements && (
          <div className="measurements-grid">
            {Object.entries(measurements).map(([key, value]) => {
              // Convert cm to inches (1 cm = 0.393701 inches)
              const inches = (value * 0.393701).toFixed(1);
              // Replace underscores with spaces in the measurement name
              const displayName = key.replace(/_/g, ' ');
              return (
                <div key={key} className="measurement-card">
                  <h3>{displayName}</h3>
                  <div className="measurement-value">
                    <span className="value">{inches} inches</span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </section>
    </div>
  );
}

export default App;