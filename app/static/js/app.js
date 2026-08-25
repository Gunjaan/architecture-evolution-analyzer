const form = document.querySelector("#analysis-form");
const statusMessage = document.querySelector("#analysis-status");
const submitButton = document.querySelector("#submit-button");
const results = document.querySelector("#results");

const escapeHtml = (value) => String(value).replace(/[&<>'"]/g, (character) => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;",
}[character]));

function setStatus(message, isError = false) {
  statusMessage.textContent = message;
  statusMessage.classList.toggle("error", isError);
}

function renderReport(report) {
  document.querySelector("#report-title").textContent = report.repository;
  const metrics = [
    [report.total_commits, "Git commits"],
    [report.snapshots_analyzed, "Historical snapshots"],
    [report.supported_files, "Source files"],
    [report.drift_events.length, "Drift events"],
  ];
  document.querySelector("#summary-metrics").innerHTML = metrics.map(([value, label]) =>
    `<div class="metric"><span class="metric-value">${escapeHtml(value)}</span><span class="metric-label">${escapeHtml(label)}</span></div>`,
  ).join("");

  document.querySelector("#languages").innerHTML = Object.entries(report.languages).length
    ? Object.entries(report.languages).map(([language, count]) => `<span class="pill">${escapeHtml(language)} · ${escapeHtml(count)}</span>`).join("")
    : "No supported source files found.";

  document.querySelector("#drift-events").innerHTML = report.drift_events.length
    ? report.drift_events.map((event) => `<article class="event ${escapeHtml(event.severity)}"><strong>${escapeHtml(event.type.replaceAll("_", " "))}</strong><p>${escapeHtml(event.message)} (commit ${escapeHtml(event.commit.slice(0, 8))})</p></article>`).join("")
    : "No configured drift thresholds were crossed.";

  document.querySelector("#hotspots").innerHTML = report.hotspots.length
    ? report.hotspots.map((hotspot) => `<tr><td>${escapeHtml(hotspot.path)}</td><td>${escapeHtml(hotspot.latest_lines)}</td><td>${Number(hotspot.line_change_percent).toFixed(1)}%</td><td>${escapeHtml(hotspot.latest_functions)}</td><td>${escapeHtml(hotspot.latest_branches)}</td><td>${escapeHtml(hotspot.score)}</td></tr>`).join("")
    : '<tr><td colspan="6">No evolving hotspots detected.</td></tr>';

  const aiSection = document.querySelector("#ai-section");
  if (report.ai_explanation) {
    document.querySelector("#ai-explanation").textContent = report.ai_explanation;
    aiSection.hidden = false;
  } else {
    aiSection.hidden = true;
  }
  results.hidden = false;
}

async function pollAnalysis(jobId) {
  const response = await fetch(`/api/analyses/${jobId}`);
  const job = await response.json();
  if (!response.ok) throw new Error(job.detail || "Unable to read analysis status.");
  if (job.status === "completed") return job.report;
  if (job.status === "failed") throw new Error(job.error || "Analysis failed.");
  setStatus(job.status === "queued" ? "Analysis is queued…" : "Analyzing Git history…");
  await new Promise((resolve) => window.setTimeout(resolve, 1500));
  return pollAnalysis(jobId);
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!form.reportValidity()) return;
  submitButton.disabled = true;
  results.hidden = true;
  setStatus("Submitting repository…");
  try {
    const payload = {
      repository_url: document.querySelector("#repository-url").value,
      snapshot_count: Number(document.querySelector("#snapshot-count").value),
    };
    const response = await fetch("/api/analyses", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const job = await response.json();
    if (!response.ok) throw new Error(job.detail || "Could not start the analysis.");
    setStatus("Analysis is queued…");
    renderReport(await pollAnalysis(job.id));
    setStatus("Analysis complete.");
  } catch (error) {
    setStatus(error.message, true);
  } finally {
    submitButton.disabled = false;
  }
});
