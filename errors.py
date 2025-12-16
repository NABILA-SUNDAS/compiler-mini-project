# src/errors.py

class LexError(Exception):
    """Error thrown by the lexer (tokenization phase)."""
    pass


class ParseError(Exception):
    """Error thrown by the parser (syntax phase)."""
    pass


class SemanticError(Exception):
    """Error thrown by the semantic analyzer."""
    pass


class RuntimeErrorMC(Exception):
    """Error thrown by the virtual machine / runtime."""
    pass
