"""Domain-specific exceptions exposed by the service layer."""


class AnalysisError(RuntimeError):
    """Raised when a repository cannot be analyzed safely."""


class InvalidRepositoryUrlError(AnalysisError):
    """Raised when a submitted URL is not a supported public GitHub URL."""


class LLMUnavailableError(AnalysisError):
    """Raised when an optional LLM provider cannot complete an interpretation."""
