"""Custom exceptions for GNCMakeBridge."""


class GNCMakeBridgeError(Exception):
    """Base exception for all GNCMakeBridge errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class ParseError(GNCMakeBridgeError):
    """Raised when parsing fails."""

    def __init__(self, message: str, line: int | None = None, column: int | None = None) -> None:
        self.line = line
        self.column = column
        if line is not None:
            full_message = f"{message} (line {line}"
            if column is not None:
                full_message += f", column {column}"
            full_message += ")"
            super().__init__(full_message)
        else:
            super().__init__(message)


class GenerationError(GNCMakeBridgeError):
    """Raised when code generation fails."""

    pass


class ConversionError(GNCMakeBridgeError):
    """Raised when conversion fails."""

    pass


class ConfigurationError(GNCMakeBridgeError):
    """Raised when configuration is invalid."""

    pass


class UnsupportedFeatureError(GNCMakeBridgeError):
    """Raised when an unsupported feature is encountered."""

    pass
