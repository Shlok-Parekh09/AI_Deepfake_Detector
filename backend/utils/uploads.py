"""Bounded, chunked upload staging; no full-file copy in application memory."""
import os
import tempfile
from fastapi import HTTPException

MAX_UPLOAD_BYTES = 1024 ** 3


async def stage_upload(upload, max_bytes=MAX_UPLOAD_BYTES):
    suffix = os.path.splitext(upload.filename or 'upload')[1]
    path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as output:
            path = output.name
            total = 0
            while chunk := await upload.read(1024 * 1024):
                total += len(chunk)
                if total > max_bytes:
                    raise HTTPException(status_code=413, detail='File exceeds the 1 GB maximum.')
                output.write(chunk)
        return path
    except BaseException:
        if path and os.path.exists(path):
            os.unlink(path)
        raise
