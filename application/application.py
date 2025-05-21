from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from logging_config import setup_logging
import logging
import time
from starlette.requests import Request
from starlette.responses import Response

def create_app():
    """Cria e configura a aplicação FastAPI."""
    app = FastAPI(title="CensoEscolarAPI", version="1.0.0")

    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "https://your-frontend-domain.com"],  # Ajuste conforme necessário
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    
    logger = setup_logging()

    
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.time()
        response: Response = await call_next(request)
        duration = time.time() - start_time
        logger.info(
            f"method={request.method} path={request.url.path} "
            f"status={response.status_code} duration={duration:.3f}s "
            f"client={request.client.host}"
        )
        return response

    return app