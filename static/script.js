const form = document.getElementById('shorten-form');
const originalUrlInput = document.getElementById('original-url');
const customCodeInput = document.getElementById('custom-code');
const submitBtn = document.getElementById('submit-btn');
const errorBox = document.getElementById('error-box');
const resultCard = document.getElementById('result-card');
const shortUrlText = document.getElementById('short-url-text');
const resultOriginal = document.getElementById('result-original');
const copyBtn = document.getElementById('copy-btn');
const refreshBtn = document.getElementById('refresh-btn');
const urlsTbody = document.getElementById('urls-tbody');
const statTotalUrls = document.getElementById('stat-total-urls');
const statTotalClicks = document.getElementById('stat-total-clicks');

function showError(message){
  errorBox.textContent = message;
  errorBox.classList.remove('hidden');
}

function clearError(){
  errorBox.classList.add('hidden');
  errorBox.textContent = '';
}

function formatDate(iso){
  const d = new Date(iso);
  return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
}

async function fetchSummary(){
  try{
    const res = await fetch('/api/stats/summary');
    if(!res.ok) return;
    const data = await res.json();
    statTotalUrls.textContent = data.total_urls;
    statTotalClicks.textContent = data.total_clicks;
  }catch(e){ /* silent - non critical */ }
}

async function fetchUrls(){
  urlsTbody.innerHTML = '<tr><td colspan="5" class="empty-row">Loading…</td></tr>';
  try{
    const res = await fetch('/api/urls?limit=50');
    if(!res.ok) throw new Error('Failed to load URLs');
    const rows = await res.json();

    if(rows.length === 0){
      urlsTbody.innerHTML = '<tr><td colspan="5" class="empty-row">No links yet — shorten your first one above.</td></tr>';
      return;
    }

    urlsTbody.innerHTML = '';
    rows.forEach(row => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td class="short-code-cell"><a href="/${row.short_code}" target="_blank" rel="noopener">/${row.short_code}</a></td>
        <td class="original-url-cell" title="${row.original_url}">${row.original_url}</td>
        <td class="clicks-cell">${row.clicks}</td>
        <td class="created-cell">${formatDate(row.created_at)}</td>
        <td><button class="delete-btn" data-code="${row.short_code}" title="Delete">✕</button></td>
      `;
      urlsTbody.appendChild(tr);
    });

    urlsTbody.querySelectorAll('.delete-btn').forEach(btn => {
      btn.addEventListener('click', () => deleteUrl(btn.dataset.code));
    });
  }catch(e){
    urlsTbody.innerHTML = '<tr><td colspan="5" class="empty-row">Could not load links. Is the API running?</td></tr>';
  }
}

async function deleteUrl(code){
  try{
    const res = await fetch(`/api/urls/${code}`, { method: 'DELETE' });
    if(!res.ok) throw new Error('Delete failed');
    await Promise.all([fetchUrls(), fetchSummary()]);
  }catch(e){
    showError('Could not delete that link. Try again.');
  }
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  clearError();
  resultCard.classList.add('hidden');

  const original_url = originalUrlInput.value.trim();
  const custom_code = customCodeInput.value.trim();

  const payload = { original_url };
  if(custom_code) payload.custom_code = custom_code;

  submitBtn.disabled = true;
  submitBtn.textContent = 'Shortening…';

  try{
    const res = await fetch('/api/shorten', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();

    if(!res.ok){
      const detail = Array.isArray(data.detail)
        ? data.detail.map(d => d.msg).join(', ')
        : (data.detail || 'Something went wrong.');
      throw new Error(detail);
    }

    shortUrlText.textContent = data.short_url;
    resultOriginal.textContent = data.original_url;
    resultCard.classList.remove('hidden');
    form.reset();

    await Promise.all([fetchUrls(), fetchSummary()]);
  }catch(err){
    showError(err.message);
  }finally{
    submitBtn.disabled = false;
    submitBtn.textContent = 'Shorten';
  }
});

copyBtn.addEventListener('click', async () => {
  try{
    await navigator.clipboard.writeText(shortUrlText.textContent);
    copyBtn.textContent = 'Copied!';
    setTimeout(() => { copyBtn.textContent = 'Copy'; }, 1500);
  }catch(e){
    showError('Could not copy — please copy manually.');
  }
});

refreshBtn.addEventListener('click', () => {
  fetchUrls();
  fetchSummary();
});

fetchUrls();
fetchSummary();
