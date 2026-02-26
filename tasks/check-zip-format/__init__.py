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
    url = params["url"]

    if not url:
        raise ValueError("url is required")

    # Check if it's a local file path (file:// scheme or plain path)
    if url.startswith("file://"):
        file_path = url[7:]  # Remove file:// prefix
        return _check_local_zip(file_path)

    # Check if it's a plain local path (no scheme, exists locally)
    if not url.startswith(("http://", "https://")):
        return _check_local_zip(url)

    # Remote URL - download and check signature
    async with httpx.AsyncClient(verify=False) as client:
        # Use GET with range header to download only first 4 bytes for signature check
        # If server doesn't support range, fall back to downloading header
        try:
            # First try HEAD request to get content-length
            head_response = await client.head(url, timeout=30.0, follow_redirects=True)

            if head_response.status_code >= 400:
                raise ValueError(f"URL is not accessible (status: {head_response.status_code}): {url}")

            content_length = head_response.headers.get("content-length")
            file_size = int(content_length) if content_length else None

            # Try to get first 4 bytes to check ZIP signature
            headers = {"Range": "bytes=0-3"}
            response = await client.get(url, headers=headers, timeout=30.0, follow_redirects=True)

            if response.status_code == 206:  # Partial content - range supported
                signature = response.content
            elif response.status_code == 200:  # Full content returned (range not supported)
                signature = response.content[:4]
            else:
                raise ValueError(f"Failed to fetch file content (status: {response.status_code}): {url}")

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