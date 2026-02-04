# Sample Python Programming Notes

## Python Basics

Python is a high-level, interpreted programming language known for its simplicity and readability.

### Key Features
- Easy to learn syntax
- Dynamic typing
- Extensive standard library
- Cross-platform compatibility
- Large community support

## Data Types

### Basic Types
```python
# Numbers
integer = 42
floating = 3.14
complex_num = 1 + 2j

# Strings
name = "Alice"
message = 'Hello World'

# Boolean
is_active = True
has_error = False
```

### Collections
```python
# List - ordered, mutable
fruits = ['apple', 'banana', 'cherry']

# Tuple - ordered, immutable
coordinates = (10, 20)

# Dictionary - key-value pairs
person = {'name': 'Bob', 'age': 30}

# Set - unordered, unique elements
unique_numbers = {1, 2, 3}
```

## Control Flow

### Conditionals
```python
if score >= 90:
    grade = 'A'
elif score >= 80:
    grade = 'B'
else:
    grade = 'C'
```

### Loops
```python
# For loop
for i in range(5):
    print(i)

# While loop
count = 0
while count < 5:
    print(count)
    count += 1
```

## Functions

```python
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"

# Lambda functions
square = lambda x: x ** 2
```

## Object-Oriented Programming

```python
class Dog:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def bark(self):
        return f"{self.name} says woof!"

# Create instance
my_dog = Dog("Buddy", 3)
```

## File Operations

```python
# Reading
with open('file.txt', 'r') as f:
    content = f.read()

# Writing
with open('output.txt', 'w') as f:
    f.write("Hello, World!")
```

## Exception Handling

```python
try:
    result = 10 / 0
except ZeroDivisionError:
    print("Cannot divide by zero")
except Exception as e:
    print(f"Error: {e}")
finally:
    print("Cleanup code")
```

## Popular Libraries

- **NumPy**: Numerical computing
- **Pandas**: Data analysis
- **Matplotlib**: Data visualization
- **Scikit-learn**: Machine learning
- **Django/Flask**: Web development
- **TensorFlow/PyTorch**: Deep learning

## Best Practices

1. Follow PEP 8 style guide
2. Use meaningful variable names
3. Write docstrings for functions
4. Handle exceptions properly
5. Use virtual environments
6. Write unit tests

## Common Patterns

### List Comprehension
```python
squares = [x**2 for x in range(10)]
even_squares = [x**2 for x in range(10) if x % 2 == 0]
```

### Dictionary Comprehension
```python
squares_dict = {x: x**2 for x in range(5)}
```

### Generator Expression
```python
sum_of_squares = sum(x**2 for x in range(1000000))
```

## Conclusion

Python's simplicity and powerful features make it an excellent choice for beginners and experts alike. Practice regularly to master these concepts!
