"""Structured application exceptions and their FastAPI error handlers."""

import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

logger = logging.getLogger("evidencerag")


class AppError(Exception):
    """Base class for expected application errors with a stable error code."""

    code: str = "APP_ERROR"
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class InvalidFileTypeError(AppError):
    code = "INVALID_FILE_TYPE"
    status_code = status.HTTP_400_BAD_REQUEST


class FileTooLargeError(AppError):
    code = "FILE_TOO_LARGE"
    status_code = status.HTTP_413_CONTENT_TOO_LARGE


class EmptyFileError(AppError):
    code = "EMPTY_FILE"
    status_code = status.HTTP_400_BAD_REQUEST


class InvalidPdfError(AppError):
    code = "INVALID_PDF"
    status_code = status.HTTP_400_BAD_REQUEST


class DocumentNotFoundError(AppError):
    code = "DOCUMENT_NOT_FOUND"
    status_code = status.HTTP_404_NOT_FOUND


class DocumentProcessingFailedError(AppError):
    code = "DOCUMENT_PROCESSING_FAILED"
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT


class StorageError(AppError):
    code = "STORAGE_ERROR"
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


class DatabaseError(AppError):
    code = "DATABASE_ERROR"
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


class EmbeddingFailedError(AppError):
    code = "EMBEDDING_FAILED"
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


class VectorStoreError(AppError):
    code = "VECTOR_STORE_ERROR"
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


class RetrievalFailedError(AppError):
    code = "RETRIEVAL_FAILED"
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


class LLMError(AppError):
    code = "LLM_ERROR"
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE


class InvalidQuestionError(AppError):
    code = "INVALID_QUESTION"
    status_code = status.HTTP_400_BAD_REQUEST


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
        logger.warning(
            "application_error", extra={"code": exc.code, "error_message": exc.message}
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.code, "message": exc.message}},
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("unhandled_exception")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred.",
                }
            },
        )
