const urlInput = document.getElementById('urlInput');
const convertBtn = document.getElementById('convertBtn');
const outputDiv = document.getElementById('output');
const spinner = document.getElementById('spinner');

// If your backend runs at a different host/port, set it here, e.g.:
// const API_BASE = 'https://api.yourdomain.com/v1';
const API_BASE = '';

function determineDirection(url) {
  const lower = url.toLowerCase();
  if (lower.includes('spotify.com/track/')) {
    return 'spotify-to-youtube';
  }
  if (lower.includes('youtube.com/watch') || lower.includes('music.youtube.com/watch')) {
    return 'youtube-to-spotify';
  }
  return null;
}

function showSpinner() {
  spinner.style.display = 'block';
}
function hideSpinner() {
  spinner.style.display = 'none';
}

async function convert() {
  const rawUrl = urlInput.value.trim();
  outputDiv.innerHTML = '';
  const direction = determineDirection(rawUrl);

  if (!rawUrl) {
    showError('Please enter a track URL.');
    return;
  }
  if (!direction) {
    showError('Unsupported URL. Paste a valid Spotify or YouTube Music link.');
    return;
  }

  const endpoint = `/convert/${direction}`;
  const payloadKey = direction === 'spotify-to-youtube' ? 'spotify_url' : 'youtube_url';
  const payload = { [payloadKey]: rawUrl };

  showSpinner();
  try {
    const res = await fetch(API_BASE + endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      const errData = await res.json();
      throw new Error(errData.detail || 'Conversion failed.');
    }

    const data = await res.json();
    const converted = direction === 'spotify-to-youtube' ? data.youtube_music_url : data.spotify_url;
    showResult(converted);
  } catch (err) {
    showError(err.message);
  } finally {
    hideSpinner();
  }
}

function showResult(convertedUrl) {
  // Clear previous output
  outputDiv.innerHTML = '';

  // Create container
  const container = document.createElement('div');
  container.classList.add('result-container');

  // Create link element
  const link = document.createElement('a');
  link.href = convertedUrl;
  link.target = '_blank';
  link.textContent = convertedUrl;

  // Create copy‐icon button
  const copyBtn = document.createElement('button');
  copyBtn.classList.add('copy-icon');
  copyBtn.innerHTML = `
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="18"
      height="18"
      fill="currentColor"
      viewBox="0 0 16 16"
    >
      <path
        d="M10 1.5H4A1.5 1.5 0 0 0 2.5 3v9A1.5
           1.5 0 0 0 4 13.5h6A1.5 1.5 0 0 0 11.5
           12V3A1.5 1.5 0 0 0 10 1.5zM4 2h6A1 1 0 0
           1 11 3v1H3V3a1 1 0 0 1 1-1zm6 11H4a1 1 0 0
           1-1-1V5h8v7a1 1 0 0 1-1 1z"
      />
      <path
        d="M8 4.5a.5.5 0 0 1 .5.5v6.793l1.146-1.147a
           .5.5 0 1 1 .708.708l-2 2a.498.498 0 0
           1-.708 0l-2-2a.5.5 0 1 1 .708-.708L
           7.5 11.793V5a.5.5 0 0 1 .5-.5z"
      />
    </svg>
  `;

  // Create “Copied!” tooltip span
  const tooltip = document.createElement('span');
  tooltip.classList.add('tooltip');
  tooltip.textContent = 'Copied!';

  // Copy to clipboard on click
  copyBtn.addEventListener('click', () => {
    navigator.clipboard
      .writeText(convertedUrl)
      .then(() => {
        tooltip.classList.add('visible');
        setTimeout(() => tooltip.classList.remove('visible'), 1400);
      })
      .catch(() => {
        tooltip.textContent = 'Failed to copy';
        tooltip.classList.add('visible');
        setTimeout(() => {
          tooltip.classList.remove('visible');
          tooltip.textContent = 'Copied!';
        }, 1400);
      });
  });

  // Append link, copy‐icon, and tooltip
  container.appendChild(link);
  container.appendChild(copyBtn);
  container.appendChild(tooltip);
  outputDiv.appendChild(container);
}

function showError(msg) {
  outputDiv.innerHTML = `<div class="error">${msg}</div>`;
}

/* === Listeners === */
convertBtn.addEventListener('click', convert);
urlInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') {
    convert();
  }
});
