from fastapi.middleware.cors import CORSMiddleware

def create_app():
    app = FastAPI(title="CensoEscolarAPI", version="1.0.0")

    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "https://your-frontend-domain.com"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
  
    return app