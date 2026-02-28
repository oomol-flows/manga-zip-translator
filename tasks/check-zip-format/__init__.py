#region generated meta
import typing
class Inputs(typing.TypedDict):
    path: str
class Outputs(typing.TypedDict):
    is_zip: typing.NotRequired[bool]
    file_size: typing.NotRequired[float]
    file_zip_path: typing.NotRequired[str]
    file_zip_url: typing.NotRequired[str]
#endregion

import httpx
import zipfile
import os
from oocana import Context

# ZIP file magic number signature
ZIP_SIGNATURE = b'PK\x03\x04'


async def main(params: Inputs, context: Context) -> Outputs:
    url = params["path"]

    if not url:
        raise ValueError("url is required")

    # Check if it's a local file path (file:// scheme or plain path)
    if url.startswith("file://"):
        file_path = url[7:]  # Remove file:// prefix
        return _check_local_zip(file_path)

    # Check if it's a plain local path (no scheme, exists locally)
    if not url.startswith(("http://", "https://")):
        return _check_local_zip(url)

    # Remote URL - use GET with stream to minimize download
    async with httpx.AsyncClient(verify=False) as client:
        try:
            # Use GET with Range header to minimize download
            # Stream mode allows us to read only what we need
            headers = {"Range": "bytes=0-3"}
            async with client.stream("GET", url, headers=headers, timeout=30.0, follow_redirects=True) as response:
                if response.status_code >= 400:
                    raise ValueError(f"URL is not accessible (status: {response.status_code}): {url}")

                # Get content-length from headers (may be total size or partial size)
                content_range = response.headers.get("content-range")
                content_length = response.headers.get("content-length")

                # Parse file size from Content-Range header if available (e.g., "bytes 0-3/12345")
                if content_range:
                    try:
                        file_size = int(content_range.split("/")[-1])
                    except (ValueError, IndexError):
                        file_size = None
                elif content_length and response.status_code == 200:
                    # If full content returned, content-length is the total size
                    file_size = int(content_length)
                else:
                    file_size = None

                # Read only first 4 bytes for signature check
                signature = b""
                async for chunk in response.aiter_bytes(4):
                    signature += chunk
                    if len(signature) >= 4:
                        break

            # Check if signature matches ZIP format
            is_zip = signature[:4] == ZIP_SIGNATURE

            result: Outputs = {
                "is_zip": is_zip,
            }

            if file_size is not None:
                result["file_size"] = file_size

            if is_zip:
                result["file_zip_url"] = url

            return result

        except httpx.ConnectError:
            raise ValueError(f"Cannot connect to URL host: {url}")
        except httpx.TimeoutException:
            raise ValueError(f"Timeout while accessing URL: {url}")


def _check_local_zip(file_path: str) -> Outputs:
    """Check if a local file is a valid ZIP format."""
    if not os.path.exists(file_path):
        raise ValueError(f"File not found: {file_path}")

    # Get file size
    file_size = os.path.getsize(file_path)

    # Check file signature (first 4 bytes)
    with open(file_path, 'rb') as f:
        signature = f.read(4)

    is_zip = signature == ZIP_SIGNATURE

    # Additional validation: try to open as ZIP file
    if is_zip:
        try:
            with zipfile.ZipFile(file_path, 'r') as zf:
                # Test if it's a valid ZIP file
                bad_file = zf.testzip()
                if bad_file is not None:
                    # File has corruption but still a ZIP structure
                    pass
        except zipfile.BadZipFile:
            # Not a valid ZIP file despite having signature
            is_zip = False
        except Exception:
            # Other errors - still consider it a ZIP based on signature
            pass

    result: Outputs = {
        "is_zip": is_zip,
        "file_size": file_size,
    }

    if is_zip:
        result["file_zip_path"] = file_path

    return result