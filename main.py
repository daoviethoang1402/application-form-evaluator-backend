from fastapi import FastAPI
from app.api import file_router, resume_parser_router, jd_quantifier_router, grader_summarizer_router

app = FastAPI()

app.include_router(file_router.router)
app.include_router(resume_parser_router.router)
app.include_router(jd_quantifier_router.router)
app.include_router(grader_summarizer_router.router)
