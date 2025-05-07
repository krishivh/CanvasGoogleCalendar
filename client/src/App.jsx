import React, { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [courses, setCourses] = useState([]);
  const [selectedCourse, setSelectedCourse] = useState("");
  const [message, setMessage] = useState("");
  const [addedExams, setAddedExams] = useState([]);

  useEffect(() => {
    fetch("http://127.0.0.1:5000/courses")
      .then((res) => res.json())
      .then((data) => setCourses(data))
      .catch(() => setMessage("❌ Failed to fetch courses"));
  }, []);

  const handleSubmit = () => {
    if (!selectedCourse) {
      setMessage("❌ Missing course ID or name");
      return;
    }

    const course = courses.find(c => c.id === parseInt(selectedCourse));
    if (!course) {
      setMessage("❌ Selected course not found");
      return;
    }

    setMessage("⏳ Processing...");
    setAddedExams([]);

    fetch("http://127.0.0.1:5000/process", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        courseId: selectedCourse,
        courseName: course.name
      }),
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.details) {
          setAddedExams(data.details);
          setMessage(`✅ ${data.details.length} exam(s) added to your calendar!`);
        } else {
          setMessage(data.message || "❌ Something went wrong.");
        }
      })
      .catch(() => setMessage("❌ An error occurred while processing."));
  };

  return (
    <div className="App">
      <h1>📘 Select a Class</h1>

      <select onChange={(e) => setSelectedCourse(e.target.value)} defaultValue="">
        <option value="">-- Select a class --</option>
        {courses.map((course) => (
          <option key={course.id} value={course.id}>
            {course.name}
          </option>
        ))}
      </select>

      <br />
      <button onClick={handleSubmit}>Add to Google Calendar</button>

      {message && (
        <p className={message.includes("✅") ? "success" : "error"}>
          {message}
        </p>
      )}

      {addedExams.length > 0 && (
        <ul>
          {addedExams.map((exam, index) => (
            <li key={index}>
              {exam.type} on {exam.date} {exam.time ? `at ${exam.time}` : "(all day)"}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default App;
