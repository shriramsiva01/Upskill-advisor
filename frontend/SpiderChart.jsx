// SpiderChart.jsx
import React from "react";
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer } from "recharts";

export default function SpiderChart({ data }) {
  if (!data) return null;
  const chartData = data.labels.map((label, idx) => ({
    skill: label,
    Student: data.student_levels[idx],
    Job: data.job_levels[idx]
  }));

  return (
    <div style={{ width: "100%", height: 360 }}>
      <ResponsiveContainer>
        <RadarChart data={chartData}>
          <PolarGrid />
          <PolarAngleAxis dataKey="skill" />
          <PolarRadiusAxis />
          <Radar name="Student" dataKey="Student" stroke="#8884d8" fill="#8884d8" fillOpacity={0.6} />
          <Radar name="Job" dataKey="Job" stroke="#82ca9d" fill="#82ca9d" fillOpacity={0.4} />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}
