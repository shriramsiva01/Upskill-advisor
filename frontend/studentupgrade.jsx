import React, { useState, useEffect } from "react";
import axios from "axios";

function StudentUpgrade() {
  const [students, setStudents] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [selectedStudent, setSelectedStudent] = useState("");
  const [selectedJob, setSelectedJob] = useState("");
  const [studentInfo, setStudentInfo] = useState(null);
  const [recommendations, setRecommendations] = useState(null);
  const [loading, setLoading] = useState(false);

  // Load dropdown data (students & jobs) when component mounts
  useEffect(() => {
    // Fetch students
    axios.get("http://127.0.0.1:8000/students")
      .then(res => {
        console.log("student data " + res.data) ; 
        setStudents(res.data);
      })
      .catch(err => {
        console.error("Error fetching students:", err);
      });

    // Fetch job roles
    axios.get("http://127.0.0.1:8000/job_roles")
      .then(res => {
        console.log("job data " + res.data) ; 
        setJobs(res.data);
      })
      .catch(err => {
        console.error("Error fetching jobs:", err);
      });
  } , []);

  // Fetch student details when dropdown changes
  

  useEffect(() => {
    if (selectedStudent) {
      axios
        .get(`http://localhost:8000/student_info`, {
          params: { student_id: (selectedStudent) }  // ✅ cleaner way
        })
        .then((res) => {
          setStudentInfo(res.data);
        })
        .catch((err) => {
          console.error("Error fetching student info:", err);
        });
    }
  }, [selectedStudent]);

  // Handle Recommendation Button
  const getRecommendations = async () => {
    if (!selectedStudent || !selectedJob) {
      alert("Please select both a student and a target role!");
      return;
    }

    setLoading(true);
    setRecommendations(null);

    try {
      console.log(selectedStudent, selectedJob);
      const response = await fetch(`http://127.0.0.1:8000/advise/${selectedStudent}/${selectedJob}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          student_id: selectedStudent,
          target_role: selectedJob
        })
      });

      const data = await response.json();
      setRecommendations(data);
    } catch (error) {
      console.error("Error fetching recommendations:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-2xl mx-auto bg-white shadow-md rounded-lg">
      <h2 className="text-2xl font-bold mb-4">Student Upgrade Planner</h2>

      {/* Student Dropdown */}
      <div className="mb-4">
        <label className="block mb-1 font-semibold">Select Student:</label>
        <select
          value={selectedStudent}
          onChange={(e) => setSelectedStudent((e.target.value))}
          className="w-full p-2 border rounded"
        >
          <option value="">-- Choose Student --</option>
          {students.map((s) => (
            <option key={s.id} value={s.id}>
              {s.name}
            </option>
          ))}
        </select>
      </div>

      {/* Target Role Dropdown */}
      <div className="mb-4">
        <label className="block mb-1 font-semibold">Select Target Role:</label>
        <select
          value={selectedJob}
          onChange={(e) => setSelectedJob((e.target.value))}
          className="w-full p-2 border rounded"
        >
          <option value="">-- Choose Role --</option>
          {jobs.map((j) => (
            <option key={j.id} value={j.id}>
              {j.title}
            </option>
          ))}
        </select>
      </div>

      {/* Show student info */}
      {studentInfo && (
        <div className="mb-4 p-3 bg-gray-100 rounded">
          <p><strong>Current Role:</strong> {studentInfo.current_role}</p>
          <p><strong>Time Available (weeks):</strong> {studentInfo.time_available}</p>
          <p><strong>Budget Available ($):</strong> {studentInfo.cost_available}</p>
        </div>
      )}

      {/* Button to trigger recommendation */}
      <button
        onClick={getRecommendations}
        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        disabled={loading}
      >
        {loading ? "Generating..." : "Get Recommendations"}
      </button>
      {console.log(recommendations)}
      {/* Show Recommendations */}
      {recommendations && (
        <div className="mt-6 p-4 border rounded bg-green-50">
          <h3 className="text-xl font-bold mb-2">Recommended Path</h3>

         {/* 3-Course Path */}
          <ol className="list-decimal list-inside mb-3">
            {recommendations?.course_path?.map((course, idx) => (
              <li key={idx}>
                {course.title} ({course.duration_weeks} weeks)
              </li>
            ))}
          </ol>

         
          {/* Timeline 
          <p><strong>Total Duration:</strong> {recommendations.timeline} weeks</p>
          <p><strong>Total Cost:</strong> ${recommendations.total_cost}</p>*/}
          <p><strong>LLM Recommendation</strong> ${recommendations.llm_reasoning}</p>
          
        </div>
      )}
    </div>
  );
}

export default StudentUpgrade;
