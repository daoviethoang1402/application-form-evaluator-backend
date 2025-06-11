from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import file_router, resume_parser_router, jd_quantifier_router, grader_summarizer_router, task_status_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Cho phép gọi từ front-end
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(file_router.router)
app.include_router(resume_parser_router.router)
app.include_router(jd_quantifier_router.router)
app.include_router(grader_summarizer_router.router)
app.include_router(task_status_router.router)
