const state = {
  presets: [],
  jobs: [],
};

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => Array.from(document.querySelectorAll(selector));

function showPage(pageId) {
  $$(".page").forEach((page) => page.classList.toggle("active", page.id === pageId));
  $$("[data-page]").forEach((button) => button.classList.toggle("active", button.dataset.page === pageId));
}

async function fetchJson(url, options) {
  const response = await fetch(url, options);
  if (!response.ok) {
    const payload = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(payload.detail || response.statusText);
  }
  return response.json();
}

async function refreshHealth() {
  const health = await fetchJson("/api/health");
  $("#status-pill").textContent = health.status === "ok" ? "Ready" : health.status;
  $("#model-status").textContent = health.model.loaded ? "Model loaded" : "Model not loaded";
  $("#health-output").textContent = JSON.stringify(health, null, 2);
}

async function refreshSystem() {
  const system = await fetchJson("/api/system");
  $("#system-output").textContent = JSON.stringify(system, null, 2);
  const gpu = system.nvidia_smi;
  $("#gpu-summary").textContent = gpu.available
    ? `${gpu.name} - ${gpu.vram_free_gb} GB free / ${gpu.vram_total_gb} GB`
    : `GPU warning: ${gpu.error || "not detected"}`;
}

async function loadOptions() {
  const payload = await fetchJson("/api/options");
  state.presets = payload.presets;
  const select = $("#preset");
  select.innerHTML = "";
  for (const preset of state.presets) {
    const option = document.createElement("option");
    option.value = preset.key;
    option.textContent = preset.label;
    select.appendChild(option);
  }
  select.value = "balanced";
  updatePresetDescription();
}

function updatePresetDescription() {
  const selected = state.presets.find((preset) => preset.key === $("#preset").value);
  $("#preset-description").textContent = selected ? selected.description : "";
}

async function refreshJobs() {
  const payload = await fetchJson("/api/jobs");
  state.jobs = payload.jobs;
  renderJobs();
  renderResults();
  renderLogSelect();
}

function renderJobs() {
  const jobsTable = $("#jobs-table");
  const recent = $("#recent-jobs");
  const rows = state.jobs.map(renderJobRow).join("");
  jobsTable.innerHTML = rows || "<p>No jobs yet.</p>";
  recent.innerHTML = state.jobs.slice(0, 5).map(renderJobRow).join("") || "<p>No jobs yet.</p>";
}

function renderResults() {
  const completed = state.jobs.filter((job) => job.status === "completed");
  $("#results-list").innerHTML = completed.map(renderJobRow).join("") || "<p>No completed results yet.</p>";
}

function renderJobRow(job) {
  const links = [];
  if (job.download.glb) links.push(`<a href="${job.download.glb}">Download GLB</a>`);
  if (job.download.preview) links.push(`<a href="${job.download.preview}">Preview</a>`);
  if (job.download.metadata) links.push(`<a href="${job.download.metadata}">Metadata</a>`);
  links.push(`<a href="${job.download.log}" target="_blank">Log</a>`);
  return `
    <div class="job-row">
      <div>
        <strong>${escapeHtml(job.name)}</strong>
        <div><span class="status ${job.status}">${job.status}</span> ${job.progress}%</div>
        <div class="small">Mode: ${job.mode} | Preset: ${job.preset} | Created: ${job.created_at}</div>
        ${job.error ? `<div class="warning">${escapeHtml(job.error)}</div>` : ""}
        ${job.warnings?.length ? `<div class="warning">${job.warnings.map(escapeHtml).join("<br>")}</div>` : ""}
      </div>
      <div class="actions">${links.join(" ")}</div>
    </div>
  `;
}

function renderLogSelect() {
  const select = $("#log-job-select");
  const current = select.value;
  select.innerHTML = '<option value="">Select a job</option>';
  for (const job of state.jobs) {
    const option = document.createElement("option");
    option.value = job.id;
    option.textContent = `${job.name} (${job.status})`;
    select.appendChild(option);
  }
  select.value = current;
}

async function submitJob(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const mode = $("#mode").value;
  const files = Array.from($("#image").files);
  if (!files.length) return;

  const submissions = mode === "batch" ? files : [files[0]];
  for (const file of submissions) {
    const data = new FormData(form);
    data.set("image", file);
    data.set("mode", mode);
    for (const checkbox of form.querySelectorAll('input[type=\"checkbox\"]')) {
      data.set(checkbox.name, checkbox.checked ? "true" : "false");
    }
    await fetchJson("/api/jobs", { method: "POST", body: data });
  }
  form.reset();
  $("#image-preview").classList.add("hidden");
  await refreshAll();
  showPage("jobs");
}

function previewImage() {
  const file = $("#image").files[0];
  const preview = $("#image-preview");
  if (!file) {
    preview.classList.add("hidden");
    return;
  }
  preview.src = URL.createObjectURL(file);
  preview.classList.remove("hidden");
}

async function loadLog() {
  const jobId = $("#log-job-select").value;
  if (!jobId) {
    $("#log-output").textContent = "Select a job to view logs.";
    return;
  }
  const response = await fetch(`/api/jobs/${jobId}/log`);
  $("#log-output").textContent = await response.text();
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  })[char]);
}

async function refreshAll() {
  await Promise.all([refreshHealth(), refreshSystem(), refreshJobs()]);
}

document.addEventListener("DOMContentLoaded", async () => {
  $$("[data-page]").forEach((button) => button.addEventListener("click", () => showPage(button.dataset.page)));
  $$("[data-page-link]").forEach((button) => button.addEventListener("click", () => showPage(button.dataset.pageLink)));
  $("#mode").addEventListener("change", () => {
    $("#front-back-panel").classList.toggle("hidden", $("#mode").value !== "front_back");
  });
  $("#preset").addEventListener("change", updatePresetDescription);
  $("#image").addEventListener("change", previewImage);
  $("#job-form").addEventListener("submit", submitJob);
  $("#refresh-system").addEventListener("click", refreshSystem);
  $("#preload-model").addEventListener("click", async () => {
    await fetchJson("/api/model/preload", { method: "POST" });
    await refreshHealth();
  });
  $("#unload-model").addEventListener("click", async () => {
    await fetchJson("/api/model/unload", { method: "POST" });
    await refreshHealth();
  });
  $("#clear-cache").addEventListener("click", async () => {
    await fetchJson("/api/cache/clear", { method: "POST" });
    await refreshSystem();
  });
  $("#log-job-select").addEventListener("change", loadLog);

  await loadOptions();
  await refreshAll();
  window.setInterval(refreshAll, 5000);
});

