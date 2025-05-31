# Music Link Converter

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Uvicorn](https://img.shields.io/badge/Uvicorn-0.20%2B-purple.svg)](https://www.uvicorn.org/)
[![Redis](https://img.shields.io/badge/Redis-6.0%2B-red.svg)](https://redis.io/)
[![HTML5](https://img.shields.io/badge/HTML-5-orange.svg)](https://developer.mozilla.org/en-US/docs/Web/Guide/HTML/HTML5)
[![CSS3](https://img.shields.io/badge/CSS-3-blueviolet.svg)](https://developer.mozilla.org/en-US/docs/Web/CSS)
[![JavaScript](https://img.shields.io/badge/JavaScript-ES6%2B-yellow.svg)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)

A simple web application to convert Spotify music track URLs to ther YouTube Music equivalents and vice-versa. It features a Python FastAPI backend and a minimalist HTML, CSS, and JavaScript frontend.

## Features

* **Bidirectional Conversion:**
  * Convert Spotify track URLs to YouTube Music URLs.
  * convert Youtube Music track URLs to Spotify URLs.
* **Automatic Detection:** The frontend automatically determines the conversion direction based on the input URL.
* **Copy to Clipboard:** Easily copy the converted URL.

## How to Use

1. Open the web application in your browser.
2. Paste a valid Spotify track URL (e.g., `https://open.spotify.com/track/...`) or a YouTube Music URL (e.g., `https://music.youtube.com/watch?v=...`) into the input field.
3. Click the "Convert" button.
4. Click the copy icon next to the URL to copy it to your clipboard.

## Tech Stack

**Backend:**

* **Python 3.12+**
* **FastAPI:** For building the API.
* **Uvicorn:** ASGI server to run FastAPI.
* **Redis:** For rate limiting.

**Frontend:**

* **HTML5**
* **CSS3**
* **Vanilla JavaScript (ES6+)**

**DevOps/Tooling:**

* **Docker & Docker Compose (Recommended):** For local testing and simple deployments.
* **Docker Stack + GitHub Actions:** For production deployments.
