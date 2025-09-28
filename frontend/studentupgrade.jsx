import React, { useState, useEffect } from "react";
import axios from "axios";
import {
  Box,
  Card,
  CardContent,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  List,
  ListItem,
  Divider,
  CircularProgress,
  Paper,
  Stack,
} from "@mui/material";
import SkillGapChart from "./SkillGapChart";

function StudentUpgrade() {
  const [students, setStudents] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [selectedStudent, setSelectedStudent] = useState("");
  const [selectedJob, setSelectedJob] = useState("");
  const [studentInfo, setStudentInfo] = useState(null);
  const [recommendations, setRecommendations] = useState(null);
  const [loading, setLoading] = useState(false);

  // Fetch students and jobs on mount
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [studentsRes, jobsRes] = await Promise.all([
          axios.get("http://localhost:8000/students"),
          axios.get("http://localhost:8000/job_roles"),
        ]);
        setStudents(studentsRes.data);
        setJobs(jobsRes.data);
      } catch (err) {
        console.error("Error fetching students or jobs:", err);
      }
    };
    fetchData();
  }, []);

  // Fetch student info when student changes
  useEffect(() => {
    if (!selectedStudent) {
      setStudentInfo(null);
      return;
    }

    const fetchStudentInfo = async () => {
      try {
        const res = await axios.get("http://localhost:8000/student_info", {
          params: { student_id: selectedStudent },
        });
        setStudentInfo(res.data);
      } catch (err) {
        console.error("Error fetching student info:", err);
      }
    };

    fetchStudentInfo();
  }, [selectedStudent]);

  // Function to get recommendations
  const getRecommendations = async () => {
    if (!selectedStudent || !selectedJob) return;
    setLoading(true);
    setRecommendations(null);

    try {
      const { data } = await axios.post(
        `http://127.0.0.1:8000/advise/${selectedStudent}/${selectedJob}`,
        {
          student_id: selectedStudent,
          target_role: selectedJob,
        },
        { headers: { "Content-Type": "application/json" } }
      );
      setRecommendations(data);
    } catch (err) {
      console.error("Error fetching recommendations:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        p: 4,
        maxWidth: "700px",
        mx: "auto",
        bgcolor: "background.paper",
        boxShadow: 3,
        borderRadius: 2,
      }}
    >
      <Typography variant="h4" fontWeight="bold" gutterBottom>
        Student Upgrade Planner
      </Typography>

      {/* Student Dropdown */}
      <FormControl fullWidth margin="normal">
        <InputLabel>Select Student</InputLabel>
        <Select
          value={selectedStudent}
          onChange={(e) => setSelectedStudent(e.target.value)}
          label="Select Student"
        >
          <MenuItem value="">
            <em>-- Choose Student --</em>
          </MenuItem>
          {students.map((s) => (
            <MenuItem key={s.id} value={s.id}>
              {s.name}
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      {/* Target Role Dropdown */}
      <FormControl fullWidth margin="normal">
        <InputLabel>Select Target Role</InputLabel>
        <Select
          value={selectedJob}
          onChange={(e) => setSelectedJob(e.target.value)}
          label="Select Target Role"
        >
          <MenuItem value="">
            <em>-- Choose Role --</em>
          </MenuItem>
          {jobs.map((j) => (
            <MenuItem key={j.id} value={j.id}>
              {j.title}
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      {/* Student info */}
      {studentInfo && (
        <Paper
          variant="outlined"
          sx={{ p: 2, mt: 2, bgcolor: "grey.100", borderRadius: 1 }}
        >
          <Typography>
            <strong>Current Role:</strong> {studentInfo.role}
          </Typography>
          <Typography>
            <strong>Time Available (weeks):</strong> {studentInfo.max_duration_weeks}
          </Typography>
          <Typography>
            <strong>Budget Available ($):</strong> {studentInfo.budget}
          </Typography>
        </Paper>
      )}
      <SkillGapChart studentId={selectedStudent} jobId={selectedJob} />
      {/* Get Recommendations Button */}
      <Box mt={3}>
        <Button
          variant="contained"
          color="primary"
          onClick={getRecommendations}
          disabled={loading}
        >
          {loading ? <CircularProgress size={24} color="inherit" /> : "Get Recommendations"}
        </Button>
      </Box>

      {/* Recommendations */}
      {recommendations && (
        <Card sx={{ mt: 4, borderRadius: 2 }}>
          <CardContent>
            <Typography variant="h5" fontWeight="bold" gutterBottom>
              Recommended Path
            </Typography>
            
            <List>
              {recommendations?.course_path?.map((course, idx) => (
                <ListItem key={idx} sx={{ display: "list-item", pl: 2 }}>
                  {course.title} ({course.duration_weeks} weeks)
                </ListItem>
              ))}
            </List>

            <Divider sx={{ my: 2 }} />

            {recommendations.llm_reasoning.split("\n").map((line, idx) => (
              <Typography key={idx} variant="body2" gutterBottom>
                {line}
              </Typography>
            ))}  
            <Stack spacing={1}>
              <Typography variant="h6" fontWeight="bold">
                Course Coverage Metric (Top k): {recommendations["top3_coverage metric"]}
              </Typography>
              <Typography variant="body1">
                LLM Latency (ms): {recommendations["llm_latency_ms"]}
              </Typography>
              <Typography variant="body1">
                Backend Latency (ms): {recommendations["backend_latency_ms"]}
              </Typography>
            </Stack>
          </CardContent>
        </Card>
      )}
    </Box>
  );
}

export default StudentUpgrade;
