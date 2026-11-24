import http from "k6/http";
import { check, sleep } from "k6";
import { Rate, Trend } from "k6/metrics";

const readLatency = new Trend("read_latency", true);
const writeLatency = new Trend("write_latency", true);
const errors = new Rate("errors");

export const options = {
  scenarios: {
    api_mix: {
      executor: "ramping-vus",
      startVUs: 1,
      stages: [
        { duration: "10s", target: 10 },
        { duration: "30s", target: 10 },
        { duration: "10s", target: 0 },
      ],
    },
  },
  thresholds: {
    http_req_failed: ["rate<0.001"],
    errors: ["rate<0.001"],
    read_latency: ["p(95)<300"],
    write_latency: ["p(95)<500"],
  },
};

const BASE = __ENV.BASE_URL || "http://host.docker.internal:8000/api/v1";

export function setup() {
  const users = [
    "owner@acme-labs.com",
    "admin@acme-labs.com",
    "manager@acme-labs.com",
    "lead@acme-labs.com",
    "member@acme-labs.com",
  ];
  const tokens = users.map((email) => {
    const response = http.post(
      `${BASE}/auth/login`,
      JSON.stringify({ email, password: "NeatSprint!2026" }),
      { headers: { "Content-Type": "application/json" } },
    );
    check(response, { "login ok": (r) => r.status === 200 });
    return response.json("data.access_token");
  });
  const projects = http.get(`${BASE}/tasks/projects`, {
    headers: { Authorization: `Bearer ${tokens[0]}` },
  });
  const projectId = projects.json("data.0.id");
  return { tokens, projectId };
}

export default function (data) {
  const token = data.tokens[Math.floor(Math.random() * data.tokens.length)];
  const headers = {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  };
  const reads = [
    `${BASE}/tasks/projects`,
    `${BASE}/tasks/projects/${data.projectId}/backlog`,
    `${BASE}/work/timesheet`,
    `${BASE}/reports/time`,
    `${BASE}/teams`,
  ];
  const path = reads[Math.floor(Math.random() * reads.length)];
  const tokenForPath = path.includes("/reports/") ? data.tokens[0] : token;
  const read = http.get(path, {
    headers: { ...headers, Authorization: `Bearer ${tokenForPath}` },
  });
  readLatency.add(read.timings.duration);
  const ok = check(read, { "read ok": (r) => r.status === 200 });
  errors.add(!ok);
  sleep(0.2);

  if (Math.random() < 0.15) {
    const write = http.post(
      `${BASE}/tasks/backlog`,
      JSON.stringify({
        project_id: data.projectId,
        type: "TASK",
        title: `Load probe ${Date.now()}`,
      }),
      { headers },
    );
    writeLatency.add(write.timings.duration);
    const writeOk = check(write, { "write ok": (r) => r.status === 201 });
    errors.add(!writeOk);
  }
}
