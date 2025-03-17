import logging
from typing import Dict, Any, Optional, Tuple, Union
from werkzeug.exceptions import HTTPException
from flask import jsonify

logger = logging.getLogger('error_handler')

class BaseError(Exception):
    def __init__(self, message: str, field: str = None, details: Dict = None):
        super().__init__(message)
        self.message = message
        self.field = field
        self.details = details or {}

class ValidationError(BaseError):
    pass

class FileProcessingError(BaseError):
    pass

class PermissionError(BaseError):
    pass

class AppError(Exception):
    def __init__(self, message: str, status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}

class ErrorHandler:
    @staticmethod
    def handle_error(error: Exception) -> Tuple[Dict[str, Union[str, Dict]], int]:
        if isinstance(error, ValidationError):
            logger.warning(f"Validation error: {error.message}", extra={
                'field': error.field,
                'details': error.details
            })
            return {
                'error': 'Validation Error',
                'message': error.message,
                'field': error.field,
                'details': error.details
            }, 400
            
        elif isinstance(error, FileProcessingError):
            logger.error(f"File processing error: {error.message}", extra={
                'field': error.field,
                'details': error.details
            })
            return {
                'error': 'File Processing Error',
                'message': error.message,
                'field': error.field,
                'details': error.details
            }, 422
            
        elif isinstance(error, PermissionError):
            logger.error(f"Permission error: {error.message}", extra={
                'field': error.field,
                'details': error.details
            })
            return {
                'error': 'Permission Error',
                'message': error.message,
                'field': error.field,
                'details': error.details
            }, 403
            
        else:
            logger.error(f"Unexpected error: {str(error)}", exc_info=True)
            return {
                'error': 'Internal Server Error',
                'message': 'An unexpected error occurred'
            }, 500

def register_error_handlers(app):
    @app.errorhandler(Exception)
    def handle_exception(e):
        if isinstance(e, HTTPException):
            response = {
                'error': e.name,
                'message': e.description
            }
            logger.warning(f"HTTP Exception: {e.name} - {e.description}")
            return jsonify(response), e.code
            
        # Log unexpected errors with full stack trace
        logger.exception("Unexpected error occurred")
        response = {
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred'
        }
        return jsonify(response), 500

    @app.errorhandler(429)
    def handle_rate_limit_error(e):
        logger.warning(f"Rate limit exceeded: {e.description}")
        return jsonify({
            'error': 'Rate Limit Exceeded',
            'message': str(e.description)
        }), 429

    @app.errorhandler(413)
    def handle_file_too_large(e):
        logger.warning(f"File too large: {e.description}")
        return jsonify({
            'error': 'File Too Large',
            'message': 'The uploaded file exceeds the maximum allowed size'
        }), 413