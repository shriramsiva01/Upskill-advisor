// api.js
import axios from "axios";
const BASE = "http://127.0.0.1:8000";

export async function getAdvise(studentId, jobId) {
  // POST request to back-end advise endpoint
  const res = await axios.post(`${BASE}/advise/${studentId}/${jobId}`);
  return res.data;
}

export async function downloadReport(studentId, jobId) {
  const res = await axios.get(`${BASE}/report/${studentId}/${jobId}`, {
    responseType: "blob"
  });
  return res.data; // blob
}
