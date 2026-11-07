from fastapi import Request, UploadFile
from typing import Dict, Any


async def DependencyDataRequest(request: Request) -> Dict[str, Any]:
    data = {}

    # Query Params
    try:
        data.update(dict(request.query_params))
    except Exception:
        pass

    content_type = request.headers.get("content-type", "")

    # JSON Body
    if "application/json" in content_type:
        try:
            body = await request.json()
            if isinstance(body, dict):
                data.update(body)
            else:
                data["body"] = body
        except Exception:
            pass

    # FormData / Multipart
    elif "multipart/form-data" in content_type or "application/x-www-form-urlencoded" in content_type:
        try:
            form = await request.form()

            for key, value in form.multi_items():

                # فایل
                if isinstance(value, UploadFile):
                    if key not in data:
                        data[key] = value
                    else:
                        if not isinstance(data[key], list):
                            data[key] = [data[key]]
                        data[key].append(value)

                # فیلد معمولی
                else:
                    if key not in data:
                        data[key] = value
                    else:
                        if not isinstance(data[key], list):
                            data[key] = [data[key]]
                        data[key].append(value)

        except Exception:
            pass

    return data
