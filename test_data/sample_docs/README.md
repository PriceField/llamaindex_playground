# Sample Project

This is a sample project for testing LlamaIndex code search and understanding capabilities.

## Overview

This project contains sample code modules to demonstrate how LlamaIndex can index and search through codebases effectively. It includes:

- **Calculator Module**: A Python module with basic arithmetic operations
- **User Service**: A JavaScript module for user management

## Features

### Calculator Functionality
The calculator module provides:
- Basic arithmetic operations (add, subtract, multiply, divide)
- History tracking for all calculations
- Error handling for edge cases like division by zero
- Object-oriented design with a Calculator class

### User Management Service
The user service provides:
- CRUD operations for user data
- Built-in caching for improved performance
- Async/await pattern for database operations
- Input validation and error handling
- Search functionality

## Usage

### Using the Calculator

```python
from calculator import Calculator

calc = Calculator()
result = calc.calculate(10, 5, "add")
print(f"Result: {result}")  # Output: Result: 15

# View history
history = calc.get_history()
print(history)
```

### Using the User Service

```javascript
const UserService = require('./user_service');

const userService = new UserService(database);

// Create a user
const newUser = await userService.createUser({
    email: 'user@example.com',
    name: 'John Doe',
    password: 'hashed_password'
});

// Get a user
const user = await userService.getUser(userId);
```

## Code Structure

```
test_data/
├── sample_code/
│   ├── calculator.py       # Python calculator module
│   └── user_service.js     # JavaScript user service
└── sample_docs/
    └── README.md           # This documentation file
```

## Best Practices Demonstrated

1. **Clear Documentation**: All functions and classes have docstrings/JSDoc comments
2. **Error Handling**: Proper validation and error messages
3. **Type Safety**: Type hints in Python, JSDoc types in JavaScript
4. **Separation of Concerns**: Each module has a single responsibility
5. **Testability**: Code is structured for easy unit testing

## Testing with LlamaIndex

This project is designed to test LlamaIndex's ability to:

1. **Extract Code Metadata**: Identify functions, classes, and imports
2. **Understand Code Structure**: Chunk code at logical boundaries
3. **Semantic Search**: Find relevant code based on natural language queries
4. **Provide Context**: Return file paths, line numbers, and code snippets

### Sample Queries

Try asking these questions:
- "How do I add two numbers?"
- "What functions are available in the calculator?"
- "Show me the user creation logic"
- "What does the UserService class do?"
- "Find all async functions"
- "How is caching implemented?"

## License

This is sample code for testing purposes only.
