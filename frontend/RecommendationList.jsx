// RecommendationList.jsx
import React, { useEffect, useState } from "react";
import { getAdvise, downloadReport } from "../api";
import SpiderChart from "./SpiderChart";

function RecommendationList({ studentId, jobId }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!studentId || !jobId) return;
    setLoading(true);
    getAdvise(studentId, jobId)
      .then(resp => setData(resp))
      .catch(err => {
        console.error(err);
        setData(null);
      })
      .finally(() => setLoading(false));
  }, [studentId, jobId]);

  const handleDownload = async () => {
    try {
      const blob = await downloadReport(studentId, jobId);
      const url = window.URL.createObjectURL(new Blob([blob]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `plan_${studentId}_${jobId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (e) {
      console.error("Download error:", e);
    }
  };

  if (loading) return <div>Loading...</div>;
  if (!data) return <div>No data yet</div>;

  return (
    <div className="mt-4">
      <h2 className="text-xl font-semibold">Recommendations</h2>

      <div className="mt-4">
        <SpiderChart data={data.spider_chart} />
      </div>

      <div className="mt-6 grid grid-cols-1 gap-3">
        {data.recommendations.map((rec) => (
          <div key={rec.skill} className="p-4 border rounded">
            <h3 className="font-bold">{rec.skill} (Gap: {rec.gap})</h3>
            {rec.courses.map(c => (
              <div key={c.course_id} className="mt-2 ml-3">
                <div className="font-semibold">{c.title}</div>
                <div className="text-sm">Provider: {c.provider} | Duration: {c.duration} | Cost: {c.cost}</div>
                <div className="text-xs text-gray-600">Score: {c.score}</div>
              </div>
            ))}
          </div>
        ))}
      </div>

      <div className="mt-6">
        <button onClick={handleDownload} className="px-4 py-2 bg-green-600 text-white rounded">
          Download PDF Report
        </button>
      </div>

      <div className="mt-4 bg-gray-50 p-3 rounded">
        <h4 className="font-semibold">LLM Reasoning</h4>
        <pre className="whitespace-pre-wrap">{data.llm_reasoning}</pre>
      </div>
    </div>
  );
}

export default RecommendationList;
