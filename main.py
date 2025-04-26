from fastapi import FastAPI
from app.api import file_router
from app.api import resume_parser_router

app = FastAPI()

app.include_router(file_router.router, prefix="/file", tags=["File"])
app.include_router(resume_parser_router.router)
