document.addEventListener('DOMContentLoaded', () => {
    const urlInput = document.getElementById('url-input');
    const convertButton = document.getElementById('convert-button');
    const spinner = document.getElementById('spinner');
    const resultContainer = document.getElementById('result-container');
    const resultUrlElement = document.getElementById('result-url');
    const copyButton = document.getElementById('copy-button');
    const copyFeedback = document.getElementById('copy-feedback');
    const errorMessageElement = document.getElementById('error-message');

    convertButton.addEventListener('click', handleSubmit);
    urlInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            handleSubmit();
        }
    });
    copyButton.addEventListener('click', copyToClipboard);

    function showSpinner() {
        spinner.style.display = 'block';
    }

    function hideSpinner() {
        spinner.style.display = 'none';
    }

    function displayResult(url) {
        resultUrlElement.href = url;
        resultUrlElement.textContent = url;
        resultContainer.style.display = 'block';
        errorMessageElement.style.display = 'none';
        copyFeedback.textContent = ''; // Clear previous feedback
    }

    function displayError(message) {
        errorMessageElement.textContent = message;
        errorMessageElement.style.display = 'block';
        resultContainer.style.display = 'none';
    }

    async function handleSubmit() {
        const inputValue = urlInput.value.trim();
        if (!inputValue) {
            displayError('Please enter a URL.');
            return;
        }

        showSpinner();
        resultContainer.style.display = 'none';
        errorMessageElement.style.display = 'none';
        copyFeedback.textContent = '';

        let apiUrl;
        let requestBody;

        if (inputValue.includes('spotify.com')) {
            apiUrl = '/convert/spotify-to-youtube';
            requestBody = { spotify_url: inputValue };
        } else if (inputValue.includes('youtube.com') || inputValue.includes('youtu.be')) {
            apiUrl = '/convert/youtube-to-spotify';
            requestBody = { youtube_url: inputValue };
        } else {
            hideSpinner();
            displayError('Invalid URL. Please use a Spotify or YouTube link.');
            return;
        }

        try {
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody),
            });

            const data = await response.json();

            if (response.ok) {
                const convertedUrl = data.youtube_music_url || data.spotify_url;
                if (convertedUrl) {
                    displayResult(convertedUrl);
                } else {
                    // Should be caught by API's 404, but as a fallback:
                    displayError(data.detail || 'Conversion successful, but no URL returned.');
                }
            } else {
                displayError(data.detail || `Error: ${response.statusText} (Status: ${response.status})`);
            }
        } catch (error) {
            console.error('Request failed:', error);
            displayError('An network error occurred. Please try again or check the console.');
        } finally {
            hideSpinner();
        }
    }

    function copyToClipboard() {
        const urlToCopy = resultUrlElement.href;
        if (urlToCopy && urlToCopy !== '#') { // Ensure there's a valid URL
            navigator.clipboard.writeText(urlToCopy)
                .then(() => {
                    copyFeedback.textContent = 'Copied to clipboard!';
                    setTimeout(() => {
                        copyFeedback.textContent = '';
                    }, 2000);
                })
                .catch(err => {
                    console.error('Failed to copy:', err);
                    copyFeedback.textContent = 'Failed to copy.';
                     setTimeout(() => {
                        copyFeedback.textContent = '';
                    }, 2000);
                });
        }
    }
});