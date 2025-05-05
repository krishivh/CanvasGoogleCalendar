import React, { useEffect, useState } from "react";

function App() {
  const [courses, setCourses] = useState([]);
  const [selectedCourse, setSelectedCourse] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    fetch("http://127.0.0.1:5000/courses")
      .then((res) => res.json())
      .then((data) => setCourses(data))
      .catch((err) => setMessage("❌ Failed to fetch courses"));
  }, []);

  const handleSubmit = () => {
    if (!selectedCourse) {
      setMessage("❗ Please select a course first.");
      return;
    }

    fetch("http://127.0.0.1:5000/process", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ courseId: selectedCourse }),
    })
      .then((res) => res.json())
      .then((data) => setMessage(data.message))
      .catch(() => setMessage("❌ Failed to process course"));
  };

  return (
    <div style={{ padding: "2rem", fontFamily: "Arial" }}>
      <h1>📚 Select a Class to Add Exam Dates</h1>
      <select
        onChange={(e) => setSelectedCourse(e.target.value)}
        style={{ padding: "0.5rem", fontSize: "1rem", marginBottom: "1rem" }}
      >
        <option value="">-- Select a class --</option>
        {courses.map((course) => (
          <option key={course.id} value={course.id}>
            {course.name}
          </option>
        ))}
      </select>
      <br />
      <button
        onClick={handleSubmit}
        style={{ padding: "0.5rem 1rem", fontSize: "1rem" }}
      >
        Add to Google Calendar
      </button>
      <p style={{ marginTop: "1rem", fontWeight: "bold", color: "darkred" }}>
        {message}
      </p>
    </div>
  );
}

export default App;
