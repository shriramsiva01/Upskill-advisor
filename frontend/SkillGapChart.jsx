import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from "recharts";
import { Paper, Typography } from "@mui/material";
import { useEffect, useState } from "react";
import axios from "axios";

const SkillGapChart = ({ studentId, jobId }) => {
  const [skillData, setSkillData] = useState([]);

  useEffect(() => {
    axios.get(`http://127.0.0.1:8000/skill_gap/${studentId}/${jobId}`)
      .then((res) => setSkillData(res.data.skill_gap))
      .catch((err) => console.error("Error fetching skill gaps:", err));
  }, [studentId, jobId]);

  return (
    <Paper variant="outlined" sx={{ p: 2, mt: 2, bgcolor: "grey.100", borderRadius: 1 }}>
      <Typography variant="h6" gutterBottom>
        Skill Gap Analysis
      </Typography>
      <ResponsiveContainer width="100%" height={300}>
        <RadarChart cx="50%" cy="50%" outerRadius="80%" data={skillData}>
          <PolarGrid />
          <PolarAngleAxis dataKey="skill" />
          <PolarRadiusAxis />
          <Radar name="Student" dataKey="student_level" stroke="#82ca9d" fill="#82ca9d" fillOpacity={0.6} />
          <Radar name="Required" dataKey="required_level" stroke="#8884d8" fill="#8884d8" fillOpacity={0.6} />
        </RadarChart>
      </ResponsiveContainer>
    </Paper>
  );
};

export default SkillGapChart;
