"""Simple calculator module for testing LlamaIndex code search."""


def add(a, b):
    """Add two numbers together.

    Args:
        a: First number
        b: Second number

    Returns:
        Sum of a and b
    """
    return a + b


def subtract(a, b):
    """Subtract b from a.

    Args:
        a: Number to subtract from
        b: Number to subtract

    Returns:
        Difference of a and b
    """
    return a - b


def multiply(a, b):
    """Multiply two numbers.

    Args:
        a: First number
        b: Second number

    Returns:
        Product of a and b
    """
    return a * b


def divide(a, b):
    """Divide a by b.

    Args:
        a: Numerator
        b: Denominator

    Returns:
        Quotient of a and b

    Raises:
        ValueError: If b is zero
    """
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


class Calculator:
    """Calculator class with history tracking."""

    def __init__(self):
        """Initialize calculator with empty history."""
        self.history = []

    def calculate(self, a, b, operation):
        """Perform calculation and store in history.

        Args:
            a: First operand
            b: Second operand
            operation: Operation to perform ('add', 'subtract', 'multiply', 'divide')

        Returns:
            Result of the calculation

        Raises:
            ValueError: If operation is not recognized
        """
        if operation == "add":
            result = add(a, b)
        elif operation == "subtract":
            result = subtract(a, b)
        elif operation == "multiply":
            result = multiply(a, b)
        elif operation == "divide":
            result = divide(a, b)
        else:
            raise ValueError(f"Unknown operation: {operation}")

        self.history.append({
            "operation": operation,
            "operands": (a, b),
            "result": result
        })
        return result

    def get_history(self):
        """Get calculation history.

        Returns:
            List of calculation records
        """
        return self.history

    def clear_history(self):
        """Clear calculation history."""
        self.history = []
