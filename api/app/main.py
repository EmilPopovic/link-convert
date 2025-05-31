from contextlib import asynccontextmanager
import logging
import os
from typing import NoReturn
from fastapi_limiter import FastAPILimiter
from redis import asyncio as aioredis
import uvicorn
from fastapi import Body, Depends, FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi_limiter.depends import RateLimiter
from fastapi.middleware.cors import CORSMiddleware

from convert import convert_spotify_to_youtube, convert_youtube_to_spotify


LOG_FORMAT = (
    "%(asctime)s | %(levelname)-8s | %(name)s | %(filename)s:%(lineno)d | "
    "%(funcName)s() | %(threadName)s | %(message)s"
)


logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


API_PORT = int(os.getenv('API_PORT', 5555))
API_URL = os.getenv('API_URL', f'http://localhost:{API_PORT}').replace('${API_PORT}', str(API_PORT))

REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379/0')
redis = aioredis.from_url(REDIS_URL)

async def rate_limit_exceeded_callback(request: Request, _, pexpire: int) -> NoReturn:
    logger.warning(f'Rate limit exceeded for client {request.client.host if request.client else ''} on endpoint {request.url.path}')

    raise HTTPException(
        status_code=429,
        detail='Rate limit exceeded. Please try again later.',
        headers={'Retry-After': str(pexpire // 1000)}
    )

GLOBAL_RATE_LIMIT = 100
GLOBAL_RATE_LIMIT_MINUTES = 10
global_limiter = RateLimiter(
    times=GLOBAL_RATE_LIMIT,
    minutes=GLOBAL_RATE_LIMIT_MINUTES,
    callback=rate_limit_exceeded_callback
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info('Starting application')
    try:
        await FastAPILimiter.init(redis)
        yield
    finally:
        logger.info('Shutting down application')
        await redis.close()

app = FastAPI(lifespan=lifespan)
app.mount('/static', StaticFiles(directory='static'), name='static')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/')
async def serve_frontend() -> FileResponse:
    logger.info('Serving frontend')
    return FileResponse('static/index.html')


@app.get('/health')
async def health() -> dict:
    logger.info('Health check endpoint called')
    return {'status': 'ok'}


@app.get('/redis-health')
async def redis_health() -> dict:
    logger.info('Redis health check endpoint called')
    try:
        await redis.ping()
        logger.info('Redis health check passed')
        return {'status': 'ok'}
    except Exception as e:
        logger.error(f'Redis health check failed: {e}')
        return {'status': 'error', 'detail': str(e)}
    

@app.get('/favicon.ico', include_in_schema=False)
async def favicon() -> FileResponse:
    logger.info('Serving favicon')
    return FileResponse('static/favicon.ico')


@app.post('/convert/spotify-to-youtube', dependencies=[Depends(global_limiter)])
async def convert_spotify_to_youtube_endpoint(spotify_url: str = Body(..., embed=True)) -> dict:
    logger.info(f'Converting Spotify URL to YouTube: {spotify_url}')
    try:
        result = convert_spotify_to_youtube(spotify_url)
        if not result['youtube_music_url']:
            raise HTTPException(status_code=404, detail="No YouTube match found.")
        return result
    except Exception as e:
        logger.error(f"Error converting Spotify to YouTube: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/convert/youtube-to-spotify', dependencies=[Depends(global_limiter)])
async def convert_youtube_to_spotify_endpoint(youtube_url: str = Body(..., embed=True)) -> dict:
    logger.info(f'Converting YouTube URL to Spotify: {youtube_url}')
    try:
        result = convert_youtube_to_spotify(youtube_url)
        if not result['spotify_url']:
            raise HTTPException(status_code=404, detail="No Spotify match found.")
        return result
    except Exception as e:
        logger.error(f"Error converting YouTube to Spotify: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    logger.info(f'Starting uvicorn server on port {API_PORT}')
    logger.info(f'Application url is {API_URL}')
    uvicorn.run(app, host='0.0.0.0', port=API_PORT, log_level='info')
