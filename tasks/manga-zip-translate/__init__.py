#region generated meta
import typing
from typing import Any, Literal
class Inputs(typing.TypedDict):
    zip_url: str
    target_lang: typing.Literal["CHS", "CHT", "CSY", "NLD", "ENG", "FRA", "DEU", "HUN", "ITA", "JPN", "KOR", "POL", "PTB", "ROM", "RUS", "ESP", "TRK", "UKR", "VIN", "ARA", "CNR", "SRP", "HRV", "THA", "IND", "FIL"]
    colorize: bool | None
    directory: str | None
    file: str | None
    wait_timeout: float | None
    poll_interval: float | None
    max_retries: float | None
    retry_delay: float | None
class Outputs(typing.TypedDict):
    session_id: typing.NotRequired[str]
    status: typing.NotRequired[str]
    result_zip_url: typing.NotRequired[str]
    result_zip_raw_url: typing.NotRequired[str | None]
    result_zip_object_key: typing.NotRequired[str | None]
    translated_images: typing.NotRequired[int]
    total_pages: typing.NotRequired[int]
    translated_pages: typing.NotRequired[int]
#endregion

import asyncio
import httpx
from oocana import Context

FUSION_API_BASE = "https://fusion-api.oomol.com/v1"


async def _request_with_retry(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    headers: dict,
    json_body: dict = None,
    max_retries: int = 3,
    retry_delay: float = 2.0
) -> httpx.Response:
    """Execute HTTP request with retry logic."""
    last_error_msg = None

    for attempt in range(max_retries):
        try:
            if method.upper() == "GET":
                response = await client.get(url, headers=headers, timeout=30.0)
            elif method.upper() == "POST":
                response = await client.post(url, headers=headers, json=json_body, timeout=30.0)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            # Check for server errors that might be transient
            if response.status_code >= 500:
                error_msg = f"Server error: {response.status_code}"
                try:
                    error_data = response.json()
                    if error_data.get("error"):
                        error_msg = f"{error_msg} - {error_data['error']}"
                    elif error_data.get("message"):
                        error_msg = f"{error_msg} - {error_data['message']}"
                except Exception:
                    pass
                last_error_msg = error_msg
                raise httpx.HTTPStatusError(
                    error_msg,
                    request=response.request,
                    response=response
                )

            # Check for other error responses (4xx)
            if response.status_code >= 400:
                error_msg = f"HTTP error: {response.status_code}"
                try:
                    error_data = response.json()
                    if error_data.get("error"):
                        error_msg = f"{error_msg} - {error_data['error']}"
                    elif error_data.get("message"):
                        error_msg = f"{error_msg} - {error_data['message']}"
                except Exception:
                    pass
                last_error_msg = error_msg
                raise httpx.HTTPStatusError(
                    error_msg,
                    request=response.request,
                    response=response
                )

            return response

        except (httpx.ConnectError, httpx.TimeoutException) as e:
            last_error_msg = str(e)
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay * (attempt + 1))

        except httpx.HTTPStatusError as e:
            last_error_msg = str(e)
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay * (attempt + 1))

    raise RuntimeError(f"Request failed after {max_retries} retries: {last_error_msg}")


async def _validate_zip_url(client: httpx.AsyncClient, zip_url: str) -> None:
    """Validate that the ZIP URL is accessible."""
    try:
        # Use GET request with stream mode (pre-signed URLs are signed for GET, not HEAD)
        # Don't read the body - just check status code and close connection
        request = client.build_request("GET", zip_url, timeout=30.0)
        response = await client.send(request, stream=True)

        try:
            if response.status_code == 404:
                raise ValueError(f"ZIP URL not found: {zip_url}")

            if response.status_code >= 400:
                # Try to read error message from response
                error_msg = f"status: {response.status_code}"
                try:
                    # Read a small portion to check for error message
                    error_text = await response.aread()
                    error_text = error_text.decode('utf-8', errors='ignore')[:500]
                    if error_text:
                        error_msg = f"{error_msg} - {error_text}"
                except Exception:
                    pass
                raise ValueError(f"ZIP URL is not accessible ({error_msg}): {zip_url}")
        finally:
            await response.aclose()  # Close without reading body

    except httpx.ConnectError:
        raise ValueError(f"Cannot connect to ZIP URL host: {zip_url}")
    except httpx.TimeoutException:
        raise ValueError(f"Timeout while checking ZIP URL: {zip_url}")


async def _submit_task(
    client: httpx.AsyncClient,
    zip_url: str,
    target_lang: str,
    oomol_token: str,
    colorize: bool | None = None,
    directory: str | None = None,
    file: str | None = None,
    max_retries: int = 3,
    retry_delay: float = 2.0
) -> str:
    """Submit manga-zip-translate task and return session ID."""
    url = f"{FUSION_API_BASE}/manga-zip-translate/submit"
    headers = {
        "Authorization": f"Bearer {oomol_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "zip_url": zip_url,
        "config": {
            "translator": {
                "target_lang": target_lang,
                "oomol_token": oomol_token
            }
        }
    }

    if colorize is not None:
        payload["colorize"] = colorize

    if directory is not None:
        payload["directory"] = directory

    if file is not None:
        # Ensure file ends with .zip
        if not file.lower().endswith(".zip"):
            file = f"{file}.zip"
        payload["file"] = file

    last_error_msg = None

    for attempt in range(max_retries):
        try:
            response = await client.post(url, headers=headers, json=payload, timeout=30.0)

            # Handle server errors (5xx) - may be transient, retry
            if response.status_code >= 500:
                last_error_msg = f"status={response.status_code}, response={response.text}"
                if attempt < max_retries - 1:
                    print(f"[RETRY {attempt + 1}/{max_retries}] {last_error_msg}")
                    await asyncio.sleep(retry_delay * (attempt + 1))
                    continue
                raise RuntimeError(f"Task submission failed after {max_retries} retries: {last_error_msg}")

            # Handle client errors (4xx) - don't retry
            if response.status_code >= 400:
                raise RuntimeError(f"Task submission failed: status={response.status_code}, response={response.text}")

            # Success response
            result = response.json()
            print(f"[DEBUG] Submit response: {result}")

            if not result.get("success"):
                raise RuntimeError(f"Task submission failed: {result}")

            session_id = result.get("sessionID")
            if not session_id:
                raise RuntimeError(f"Task submission failed: no sessionID in response, response={result}")

            print(f"[DEBUG] Got sessionID: {session_id}")
            return session_id

        except httpx.ConnectError as e:
            last_error_msg = f"Connection error: {e}"
            if attempt < max_retries - 1:
                print(f"[RETRY {attempt + 1}/{max_retries}] {last_error_msg}")
                await asyncio.sleep(retry_delay * (attempt + 1))
            else:
                raise RuntimeError(f"Task submission failed after {max_retries} retries: {last_error_msg}")

        except httpx.TimeoutException as e:
            last_error_msg = f"Request timeout: {e}"
            if attempt < max_retries - 1:
                print(f"[RETRY {attempt + 1}/{max_retries}] {last_error_msg}")
                await asyncio.sleep(retry_delay * (attempt + 1))
            else:
                raise RuntimeError(f"Task submission failed after {max_retries} retries: {last_error_msg}")

        except RuntimeError:
            raise

    raise RuntimeError(f"Task submission failed after {max_retries} retries: {last_error_msg}")


async def _poll_state(
    client: httpx.AsyncClient,
    session_id: str,
    oomol_token: str,
    context: Context,
    wait_timeout: float,
    poll_interval: float,
    max_retries: int,
    retry_delay: float
) -> None:
    """Poll for task state until completion or timeout. Returns nothing, only reports progress."""
    url = f"{FUSION_API_BASE}/manga-zip-translate/state/{session_id}"
    print(f"[DEBUG] Poll state URL: {url}")
    print(f"[DEBUG] Polling with session_id: {session_id}")
    headers = {
        "Authorization": f"Bearer {oomol_token}"
    }

    start_time = asyncio.get_event_loop().time()

    while True:
        elapsed = asyncio.get_event_loop().time() - start_time
        if elapsed >= wait_timeout:
            raise TimeoutError(f"Task polling timed out after {wait_timeout} seconds")

        response = await _request_with_retry(
            client, "GET", url, headers, max_retries=max_retries, retry_delay=retry_delay
        )

        if response.status_code == 404:
            raise RuntimeError(f"Session not found: {session_id}")

        if response.status_code == 200:
            result = response.json()
            state = result.get("state")

            if state == "completed":
                # Task completed successfully, return to fetch result
                context.report_progress(100)
                return

            if state == "processing":
                # Task still processing - API returns progress 0-100
                # Map to overall progress 10-100 (first 10% for validation/submit)
                api_progress = result.get("progress", 0)
                # Map 0-100 to 10-100 range
                overall_progress = 10 + int(api_progress * 0.9)
                context.report_progress(overall_progress)
                await asyncio.sleep(poll_interval)
                continue

            # Any other state (failed, error, etc.) - raise error with details
            error_msg = result.get("error") or result.get("message") or "No additional details"
            raise RuntimeError(f"Task failed with state: {state} - {error_msg}")

        # Handle other status codes
        try:
            error_data = response.json()
            error_msg = error_data.get('error') or error_data.get('message') or 'Unknown error'
        except Exception:
            error_msg = response.text or 'Unknown error'
        raise RuntimeError(f"Poll state failed (status {response.status_code}): {error_msg}")


async def _fetch_result(
    client: httpx.AsyncClient,
    session_id: str,
    oomol_token: str,
    max_retries: int,
    retry_delay: float
) -> dict:
    """Fetch the final result after task completion."""
    url = f"{FUSION_API_BASE}/manga-zip-translate/result/{session_id}"
    headers = {
        "Authorization": f"Bearer {oomol_token}"
    }

    response = await _request_with_retry(
        client, "GET", url, headers, max_retries=max_retries, retry_delay=retry_delay
    )

    if response.status_code == 404:
        raise RuntimeError(f"Session not found: {session_id}")

    if not response.is_success:
        # Handle error status codes with server error message
        try:
            error_msg = response.json()
        except Exception:
            error_msg = response.text or 'Unknown error'
        raise RuntimeError(f"Fetch result failed (status {response.status_code}): {error_msg}")

    result = response.json()

    if not result.get("success"):
        raise RuntimeError(f"Failed to fetch result: {result}")

    return result.get("data", {})


async def main(params: Inputs, context: Context) -> Outputs:
    zip_url = params["zip_url"]
    target_lang = params["target_lang"]
    colorize = params.get("colorize")
    directory = params.get("directory")
    file = params.get("file")
    wait_timeout = params.get("wait_timeout") or 2400
    poll_interval = params.get("poll_interval") or 5
    max_retries = int(params.get("max_retries") or 3)
    retry_delay = params.get("retry_delay") or 2

    if not zip_url:
        raise ValueError("zip_url is required")

    # Get OOMOL token for authentication
    oomol_token = await context.oomol_token()

    async with httpx.AsyncClient() as client:
        # Step 1: Validate ZIP URL exists
        context.report_progress(2)
        await _validate_zip_url(client, zip_url)

        # Step 2: Submit task
        context.report_progress(5)
        session_id = await _submit_task(
            client, zip_url, target_lang, oomol_token,
            colorize=colorize,
            directory=directory,
            file=file,
            max_retries=max_retries,
            retry_delay=retry_delay
        )
        context.report_progress(10)

        # Output session_id immediately after getting it
        context.output("session_id", session_id)

        # Step 3: Poll for task completion (using state endpoint)
        await _poll_state(
            client, session_id, oomol_token, context,
            wait_timeout, poll_interval, max_retries, retry_delay
        )

        # Step 4: Fetch the final result
        data = await _fetch_result(
            client, session_id, oomol_token, max_retries, retry_delay
        )

        # Output each result as soon as we have it
        context.output("status", data.get("status", ""))
        context.output("result_zip_url", data.get("resultZipURL", ""))
        context.output("result_zip_raw_url", data.get("resultZipRawURL"))
        context.output("result_zip_object_key", data.get("resultZipObjectKey"))
        context.output("translated_images", int(data.get("translatedImages", 0)))
        context.output("total_pages", int(data.get("totalPages", 0)))
        context.output("translated_pages", int(data.get("translatedPages", 0)))

        return {
            "session_id": session_id,
            "status": data.get("status", ""),
            "result_zip_url": data.get("resultZipURL", ""),
            "result_zip_raw_url": data.get("resultZipRawURL"),
            "result_zip_object_key": data.get("resultZipObjectKey"),
            "translated_images": int(data.get("translatedImages", 0)),
            "total_pages": int(data.get("totalPages", 0)),
            "translated_pages": int(data.get("translatedPages", 0))
        }