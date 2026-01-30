import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.chat import router as chat_router
from app.auth.auth_router import router as auth_router
from app.routes.select_llm import router as select_llm_router

# ----------------------------------
# Logging
# ----------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ----------------------------------
# App
# ----------------------------------
app = FastAPI(title="Multi-LLM Chat")

# ----------------------------------
# CORS
# ----------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten later if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------
# Routers
# ----------------------------------
app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(select_llm_router)

# ----------------------------------
# Health Check
# ----------------------------------
@app.get("/")
def health():
    return {"status": "Backend running successfully"}
