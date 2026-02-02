import uuid as uuid_lib
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from .utils.gemini import upload_file_to_gemini
from .utils.supabase import (
    save_resume,
    get_resume as fetch_resume,
    delete_resume as remove_resume,
)

router = APIRouter(prefix="/api", tags=["resume"])


@router.post("/resume/upload")
async def upload_resume(file: UploadFile = File(...), uuid: str = Form(None)):
    try:
        gemini_file = await upload_file_to_gemini(file)

        # Use uuid from request if provided, otherwise generate a random UUID
        thread_id = uuid if uuid else str(uuid_lib.uuid4())

        # Save the resume file to Supabase
        file_name = file.filename or "resume.pdf"
        await save_resume(
            thread_id=thread_id, file_name=file_name, resume_file=gemini_file
        )

        return JSONResponse(
            content={"message": "Resume uploaded successfully!"}, status_code=200
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {e}")


@router.get("/resume/{thread_id}")
async def get_resume(thread_id: str):
    resume = await fetch_resume(thread_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return JSONResponse(
        content={"name": resume[0]["file_name"], "contentType": resume[0]["mime_type"]},
        status_code=200,
    )


@router.delete("/resume/{thread_id}")
async def delete_resume(thread_id: str):
    try:
        await remove_resume(thread_id)
        return JSONResponse(
            content={"message": "Resume deleted successfully!"}, status_code=200
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting resume: {e}")
