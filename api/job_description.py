import uuid as uuid_lib
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from .utils.gemini import upload_file_to_gemini
from .utils.supabase import (
    save_job_description,
    get_job_description as fetch_job_description,
    delete_job_description as remove_job_description
)

router = APIRouter(prefix="/api", tags=["job-description"])


@router.post("/job-description/upload")
async def upload_job_description(file: UploadFile = File(...), uuid: str = Form(None)):
    try:
        gemini_file = await upload_file_to_gemini(file)
        
        # Use uuid from request if provided, otherwise generate a random UUID
        thread_id = uuid if uuid else str(uuid_lib.uuid4())
        
        # Save the job description file to Supabase
        file_name = file.filename or "job_description.pdf"
        await save_job_description(thread_id=thread_id, file_name=file_name, job_description_file=gemini_file)
        
        return JSONResponse(content={"message": "Job description uploaded successfully!"}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {e}")


@router.get("/job-description/{thread_id}")
async def get_job_description(thread_id: str):
    job_description = await fetch_job_description(thread_id)
    if not job_description:
        raise HTTPException(status_code=404, detail="Job description not found")
    return JSONResponse(content={"name": job_description[0]["file_name"], "contentType": job_description[0]["mime_type"]}, status_code=200)


@router.delete("/job-description/{thread_id}")
async def delete_job_description(thread_id: str):
    try:
        await remove_job_description(thread_id)
        return JSONResponse(content={"message": "Job description deleted successfully!"}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting job description: {e}")
