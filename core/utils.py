import hashlib
import os
from core.models import File as CoreFile
from core.views import Storage
import uuid

# TODO: maybe change this into multi file type upload in the future
def upload_mp3_to_s3(file_obj, uploader, folder="recitations"):
    """
    Uploads an MP3 file to S3 and creates a CoreFile record.
    Returns the CoreFile instance.
    Raises ValueError if file type is not mp3.
    """
    # Calculate file hash
    sha256_hash = hashlib.sha256()
    for chunk in file_obj.chunks():
        sha256_hash.update(chunk)
    file_hash = sha256_hash.hexdigest()
    file_obj.seek(0)

    # Check for duplicate file
    existing_file = CoreFile.objects.filter(file_hash=file_hash).first()
    if existing_file:
        return existing_file

    # Get file extension and validate
    original_filename = file_obj.name
    _, ext = os.path.splitext(original_filename)
    ext = ext[1:].lower()
    if ext != "mp3":
        raise ValueError("Invalid file type. Expected mp3")

    # Generate UUID for the file
    file_uuid = str(uuid.uuid4())
    new_filename = f"{file_uuid}.{ext}"

    # Save file to S3 with public access in specified folder
    storage = Storage()
    storage.location = folder
    storage.save(new_filename, file_obj)

    # Create file record in database
    new_file = CoreFile.objects.create(
        format=ext,
        size=file_obj.size,
        s3_uuid=file_uuid,
        upload_name=original_filename,
        file_hash=file_hash,
        uploader=uploader,
    )
    return new_file
 