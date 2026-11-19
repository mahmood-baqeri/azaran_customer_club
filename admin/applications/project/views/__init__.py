# Path: applications/project/views/__init__.py

# applications/project/views/__init__.py

from .project_view import (
    project_attachment_delete,
    project_attachment_upload,
    project_approve_action,
    project_colleague_add,
    project_colleague_delete,
    project_create,
    project_delete,
    project_detail,
    project_export,
    project_index,
    project_reject_action,
    project_update,
)

__all__ = [
    "project_index", "project_export",
    "project_create", "project_update", "project_detail", "project_delete",
    "project_approve_action", "project_reject_action",
    "project_colleague_add", "project_colleague_delete",
    "project_attachment_upload", "project_attachment_delete",
]