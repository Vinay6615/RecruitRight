// Fetch results and render styled table, allow download txt
document.addEventListener('DOMContentLoaded', async () => {
  const tbody = document.getElementById('resultsBody');
  const downloadBtn = document.getElementById('downloadBtn');

  async function loadResults() {
    tbody.innerHTML = '<tr><td colspan="7">Loading...</td></tr>';

    try {
      const res = await fetch('/api/resume/results');
      const data = await res.json();

      if (!Array.isArray(data) || data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7">No results yet. Upload resumes and submit a job description.</td></tr>';
        return;
      }

      tbody.innerHTML = '';
      data.forEach((c, i) => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>${i + 1}</td>
          <td>${c.name}</td>
          <td class="score">${Number(c.score * 2.5).toFixed(2)}</td>
          <td>${c.education !== undefined ? c.education + '%' : '-'}</td>
          <td>${c.keywords !== undefined ? c.keywords + '%' : '-'}</td>
         
        `;
        tbody.appendChild(tr);
      });
    } catch (err) {
      tbody.innerHTML = '<tr><td colspan="7">Error loading results</td></tr>';
      console.error(err);
    }
  }

  loadResults();

  // --- Download TXT Report ---
  if (downloadBtn) {
    downloadBtn.addEventListener('click', async () => {
      try {
        const res = await fetch('/api/resume/results');
        const data = await res.json();
        let lines = [
          'RecruitRight - Candidate Ranking Report',
          '--------------------------------------',
          'Rank\tName\tTotal%\tEducation%\tKeywords%\t'
        ];
        data.forEach((c, i) => {
          lines.push(
            `${i + 1}\t${c.name}\t${c.score}\t${c.education || ''}\t${c.keywords || ''}`
          );
        });
        const blob = new Blob([lines.join('\n')], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'RecruitRight_Results.txt';
        a.click();
        URL.revokeObjectURL(url);
      } catch (err) {
        alert('Error downloading report.');
        console.error(err);
      }
    });
  }
});
