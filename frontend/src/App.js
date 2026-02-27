import React, { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!file) {
      alert("Please select a PDF file");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("patient_name", "Saivenkat");
    formData.append("gender", "male");

    try {
      setLoading(true);
      const res = await axios.post(
        "http://127.0.0.1:8000/analyze",
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      );
      setData(res.data);
      setLoading(false);
    } catch (err) {
      console.error(err);
      alert("Error analyzing report");
      setLoading(false);
    }
  };

  const getStatusClass = (status) => {
    if (status === "high") return "card high";
    if (status === "low") return "card low";
    return "card normal";
  };

  return (
    <div className="container">
      <h1 className="title">🧠 AI Lab Report Analyzer</h1>

      {/* Upload Section */}
      <div className="upload-box">
        <label className="file-label">
          <input
            type="file"
            accept=".pdf"
            onChange={(e) => setFile(e.target.files[0])}
            hidden
          />
          📂 Choose PDF
        </label>

        <button className="analyze-btn" onClick={handleUpload}>
          {loading ? "Analyzing..." : "🚀 Analyze Report"}
        </button>
      </div>

      {/* Summary Section */}
      {data && (
        <>
          <div className="summary-box">
            <h2>📝 Patient Summary</h2>
            <p>{data.summary}</p>
          </div>

          <h2 className="section-title">📊 Biomarker Analysis</h2>

          <div className="grid">
            {Object.entries(data.biomarkers).map(([name, details]) => (
              <div key={name} className={getStatusClass(details.status)}>
                <h3>{name}</h3>
                <p>
                  <strong>Value:</strong> {details.value} {details.unit}
                </p>
                <p>
                  <strong>Reference:</strong> {details.range}
                </p>
                <p className="desc">{details.plain_english}</p>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

export default App;