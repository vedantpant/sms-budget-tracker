# exceptions.py — Custom Exception Hierarchy

class BudgetTrackerError(Exception):
    """Base exception"""
    pass

# Transport
class TransportError(BudgetTrackerError): pass
class SupabaseConnectionError(TransportError): pass
class SupabaseTimeoutError(TransportError): pass

# Parsing
class ParsingError(BudgetTrackerError): pass
class UnknownSMSFormatError(ParsingError):
    def __init__(self, sms_body):
        self.sms_body = sms_body[:100]
        super().__init__(f"No regex matched: {self.sms_body}...")

class InvalidAmountError(ParsingError): pass
class MissingFieldError(ParsingError):
    def __init__(self, field):
        super().__init__(f"Missing field: {field}")

# Categorization
class CategorizationError(BudgetTrackerError): pass
class OllamaConnectionError(CategorizationError): pass
class OllamaTimeoutError(CategorizationError): pass
class OllamaInvalidResponseError(CategorizationError):
    def __init__(self, response):
        super().__init__(f"Invalid response: {str(response)[:200]}")

class CategoryNotFoundError(CategorizationError):
    def __init__(self, merchant):
        self.merchant = merchant
        super().__init__(f"Cannot categorize: {merchant}")

# Storage
class StorageError(BudgetTrackerError): pass
class ExcelWriteError(StorageError): pass
class ExcelLockedError(ExcelWriteError): pass
class ExcelCorruptError(ExcelWriteError): pass
class CategoryMapWriteError(StorageError): pass

# Duplicates
class DuplicateError(BudgetTrackerError): pass
class DuplicateSMSError(DuplicateError):
    def __init__(self, sms_hash):
        super().__init__(f"Duplicate SMS: {sms_hash[:16]}")

class DuplicateTransactionError(DuplicateError):
    def __init__(self, txn_id):
        super().__init__(f"Duplicate txn: {txn_id}")

# Network
class NetworkError(BudgetTrackerError): pass
class RetryExhaustedError(NetworkError):
    def __init__(self, component, max_retries):
        super().__init__(f"{component}: failed after {max_retries} retries")

# Circuit Breaker
class CircuitBreakerOpenError(BudgetTrackerError):
    def __init__(self, component):
        super().__init__(f"Circuit breaker OPEN for {component}")