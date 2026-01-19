from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..auth import get_current_user
from ..models.database_models import User
from ..vectorstore import vector_manager
from ..encryption import decrypt_api_key
from ..storage import storage_manager

router = APIRouter(prefix="/study-guide", tags=["Study Guide"])


@router.get("/status")
async def get_study_guide_status(
    current_user: User = Depends(get_current_user)
):
    """Check if the current user has uploaded a study guide and return file info."""
    filename = None
    file_size = None
    word_count = None

    if current_user.has_study_guide:
        # Get file info from Supabase Storage
        file_info = storage_manager.get_file_info(current_user.id)
        if file_info:
            filename = file_info["filename"]
            file_size = file_info["file_size"]
            word_count = file_info["word_count"]

    return {
        "has_study_guide": current_user.has_study_guide,
        "user_id": current_user.id,
        "filename": filename,
        "file_size": file_size,
        "word_count": word_count
    }


@router.post("/upload")
async def upload_study_guide(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a study guide text file. The file will be vectorized for use in chat/practice."""

    # Check if user has set an OpenAI API key
    if not current_user.encrypted_openai_key:
        raise HTTPException(
            status_code=403,
            detail="Please set your OpenAI API key before uploading a study guide"
        )

    # Validate file type
    if not file.filename.endswith('.txt'):
        raise HTTPException(status_code=400, detail="Only .txt files are allowed")

    # Decrypt the API key
    openai_api_key = decrypt_api_key(current_user.encrypted_openai_key)

    try:
        # Read file content
        content = await file.read()

        # Decode and validate text
        try:
            text_content = content.decode('utf-8')
            word_count = len(text_content.split())
        except UnicodeDecodeError:
            raise HTTPException(status_code=400, detail="File must be valid UTF-8 text")

        # Upload to Supabase Storage
        storage_manager.upload_file(current_user.id, file.filename, content)

        # Import text splitter
        from langchain.text_splitter import RecursiveCharacterTextSplitter

        # Split text into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )

        chunks = text_splitter.split_text(text_content)

        # Delete existing documents for this user (if any)
        try:
            vector_manager.delete_user_documents(current_user.id, openai_api_key)
        except Exception:
            pass  # No existing documents to delete

        # Add new documents with user_id metadata
        vector_manager.add_documents_for_user(
            user_id=current_user.id,
            texts=chunks,
            openai_api_key=openai_api_key,
            metadatas=[{"source": file.filename, "chunk_index": i} for i in range(len(chunks))]
        )

        # Update user's has_study_guide flag
        current_user.has_study_guide = True
        db.commit()

        return {
            "message": "Study guide uploaded and processed successfully",
            "filename": file.filename,
            "word_count": word_count,
            "chunks_created": len(chunks)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process study guide: {str(e)}")
