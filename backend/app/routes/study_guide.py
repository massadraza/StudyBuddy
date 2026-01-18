from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..auth import get_current_user
from ..models.database_models import User
from ..vectorstore import vector_manager
import os
from pathlib import Path

router = APIRouter(prefix="/study-guide", tags=["Study Guide"])

# Directory to store uploaded study guides
UPLOAD_DIR = Path("uploaded_study_guides")
UPLOAD_DIR.mkdir(exist_ok=True)

    
@router.get("/status")
async def get_study_guide_status(
    current_user: User = Depends(get_current_user)
):
    """Check if the current user has uploaded a study guide and return file info."""
    user_dir = UPLOAD_DIR / str(current_user.id)

    # Find the uploaded study guide file (if any)
    filename = None
    file_size = None
    word_count = None

    if current_user.has_study_guide and user_dir.exists():
        # Look for .txt files in user directory
        txt_files = list(user_dir.glob("*.txt"))
        if txt_files:
            study_file = txt_files[0]  # Get the first (should be only) txt file
            filename = study_file.name
            file_size = study_file.stat().st_size

            # Read file to get word count
            try:
                with open(study_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    word_count = len(content.split())
            except Exception:
                word_count = None

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
    # Validate file type
    if not file.filename.endswith('.txt'):
        raise HTTPException(status_code=400, detail="Only .txt files are allowed")

    # Create user-specific directory
    user_dir = UPLOAD_DIR / str(current_user.id)
    user_dir.mkdir(exist_ok=True)

    # Save the uploaded file
    file_path = user_dir / file.filename

    try:
        # Read and save file content
        content = await file.read()

        # Save to disk
        with open(file_path, 'wb') as f:
            f.write(content)

        # Decode and validate text
        try:
            text_content = content.decode('utf-8')
            word_count = len(text_content.split())
        except UnicodeDecodeError:
            raise HTTPException(status_code=400, detail="File must be valid UTF-8 text")

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
            vector_manager.delete_user_documents(current_user.id)
        except Exception:
            pass  # No existing documents to delete

        # Add new documents with user_id metadata
        vector_manager.add_documents_for_user(
            user_id=current_user.id,
            texts=chunks,
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
        # Clean up the file if processing failed
        if file_path.exists():
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Failed to process study guide: {str(e)}")
