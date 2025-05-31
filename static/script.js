const urlInput = document.getElementById('urlInput');
const convertBtn = document.getElementById('convertBtn');
const outputDiv = document.getElementById('output');
const API_BASE = ''

function determineDirection(url) {
  const lowerUrl = url.toLowerCase();
  if (lowerUrl.includes('spotify.com/track/')) {
    return 'spotify-to-youtube';
  } else if (
    lowerUrl.includes('youtube.com/watch') ||
    lowerUrl.includes('music.youtube.com/watch')
  ) {
    return 'youtube-to-spotify';
  } else {
    return null;
  }
}

async function convert() {
  const url = urlInput.value.trim();
  outputDiv.innerHTML = '';

  if (!url) {
    showError('Please enter a valid URL.');
    return;
  }

  const direction = determineDirection(url);
  if (!direction) {
    showError('Unsupported URL format. Please enter a Spotify or YouTube Music track URL.');
    return;
  }

  const endpoint = `/convert/${direction}`;
  const payloadKey = direction === 'spotify-to-youtube' ? 'spotify_url' : 'youtube_url';
  const payload = {};
  payload[payloadKey] = url;

  try {
    const response = await fetch(API_BASE + endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Conversion failed');
    }

    const data = await response.json();
    const convertedUrl =
      direction === 'spotify-to-youtube' ? data.youtube_music_url : data.spotify_url;

    showResult(`<a href="${convertedUrl}" target="_blank">${convertedUrl}</a>`);
  } catch (err) {
    showError(err.message);
  }
}

function showResult(htmlContent) {
  outputDiv.innerHTML = `<div class="result">${htmlContent}</div>`;
}

function showError(message) {
  outputDiv.innerHTML = `<div class="error">${message}</div>`;
}

convertBtn.addEventListener('click', convert);
urlInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') {
    convert();
  }
});
