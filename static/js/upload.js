// Handle resume uploads and analysis
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("uploadForm");
  const out = document.getElementById("uploadStatus");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    out.className = "status";
    out.textContent = "⏳ Uploading... Please wait.";

    const fd = new FormData();
    fd.append("jd", document.getElementById("jd").value);
    fd.append("keywords", document.getElementById("keywords").value);

    const fileInput = document.getElementById("resumeFiles");
    const folderInput = document.getElementById("resumeFolder");
    const files = [...fileInput.files, ...folderInput.files];

    if (files.length === 0) {
      out.textContent = "⚠️ Please select at least one file or folder.";
      out.classList.add("error");
      return;
    }

    files.forEach((f) => fd.append("resumes", f, f.name));

    try {
      const res = await fetch("/api/resume/upload", {
        method: "POST",
        body: fd
      });
      const data = await res.json();

      if (data.status === "ok") {
        out.innerHTML = `✅ ${data.results.length} resumes processed successfully.<br>
                         <a href="/results" style="color:#0b57a6;text-decoration:none;font-weight:600;">View Results →</a>`;
        out.classList.add("success");
      } else {
        out.textContent = "❌ Upload failed. Please try again.";
        out.classList.add("error");
      }
    } catch (err) {
      console.error(err);
      out.textContent = "🚫 Server error. Please check backend logs.";
      out.classList.add("error");
    }
  });
});
