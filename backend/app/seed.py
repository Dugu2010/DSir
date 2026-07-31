"""
Seed data for DSir platform.
Creates realistic courses, modules, lessons, exercises, and achievements.
Run: python -m app.seed
"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from app.database import async_session_factory, engine, Base
from app.models import (
    User, UserStats, Category, TechnologyStack, Course, Module,
    Lesson, Exercise, ExerciseHint, Quiz, Question, QuestionOption,
    Achievement, FeatureFlag, ContentStatus, DifficultyLevel,
    ExerciseType, ExerciseDifficulty, QuestionType,
    AchievementCategory,
)
from app.utils.security import hash_password
from datetime import datetime, timezone
from uuid import uuid4


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as db:
        # Check if already seeded
        result = await db.execute(select(User).limit(1))
        if result.scalar_one_or_none():
            print("Database already seeded. Skipping.")
            return

        print("Seeding database...")

        # ── Admin User ───────────────────────────────────────
        admin = User(
            id=uuid4(),
            email="admin@dsir.dev",
            username="admin",
            display_name="DSir Admin",
            password_hash=hash_password("Admin@123!"),
            role="superadmin",
            email_verified=True,
            is_active=True,
        )
        db.add(admin)
        db.add(UserStats(user_id=admin.id))

        # Demo student
        demo_user = User(
            id=uuid4(),
            email="demo@dsir.dev",
            username="demo_student",
            display_name="Alex Chen",
            password_hash=hash_password("Demo@123!"),
            role="student",
            email_verified=True,
            is_active=True,
            bio="Aspiring software engineer learning Python and web development.",
        )
        db.add(demo_user)
        db.add(UserStats(
            user_id=demo_user.id,
            total_xp=1250,
            current_level=5,
            current_streak=7,
            longest_streak=14,
            lessons_completed=12,
            exercises_completed=28,
        ))

        # ── Categories ───────────────────────────────────────
        categories = {}
        cat_data = [
            ("programming", "Programming Languages", "Core programming language courses", "code"),
            ("web", "Web Development", "Frontend and backend web development", "globe"),
            ("data", "Data Science & AI", "Data science, ML, and AI courses", "brain"),
            ("devops", "DevOps & Cloud", "Infrastructure, deployment, and cloud", "server"),
            ("security", "Cyber Security", "Security fundamentals and advanced", "shield"),
        ]
        for slug, name, desc, icon in cat_data:
            cat = Category(name=name, slug=slug, description=desc, icon=icon)
            db.add(cat)
            categories[slug] = cat

        # ── Technology Stacks ────────────────────────────────
        techs = {}
        tech_data = [
            ("python", "Python", "prog"), ("javascript", "JavaScript", "prog"),
            ("html", "HTML", "web"), ("css", "CSS", "web"),
            ("react", "React", "web"), ("nextjs", "Next.js", "web"),
            ("typescript", "TypeScript", "prog"), ("nodejs", "Node.js", "web"),
            ("fastapi", "FastAPI", "web"), ("django", "Django", "web"),
            ("postgresql", "PostgreSQL", "data"), ("mongodb", "MongoDB", "data"),
            ("docker", "Docker", "devops"), ("git", "Git", "devops"),
            ("linux", "Linux", "devops"), ("sql", "SQL", "data"),
        ]
        for slug, name, cat_key in tech_data:
            tech = TechnologyStack(name=name, slug=slug, category_id=categories[cat_key].id, is_featured=True)
            db.add(tech)
            techs[slug] = tech

        # ── Courses ──────────────────────────────────────────
        courses = {}

        # Python Course
        python_course = Course(
            id=uuid4(),
            title="Python Programming: From Zero to Hero",
            slug="python-programming",
            description="Master Python from absolute basics to advanced concepts. Build real-world projects and become job-ready.",
            long_description="""## What You'll Learn

This comprehensive Python course takes you from writing your first line of code to building complex applications. Whether you're a complete beginner or looking to solidify your Python skills, this course provides everything you need.

### Why Python?
- Most popular programming language in the world
- Used by Google, Netflix, NASA, and startups everywhere
- Perfect for beginners due to readable syntax
- Powers AI, data science, web apps, and automation

### Course Structure
The course is organized into progressive modules, each building on the previous one. You'll learn through interactive lessons, hands-on exercises, quizzes, and real-world projects.""",
            learning_objectives=[
                "Write clean, idiomatic Python code",
                "Understand data types, control flow, and functions",
                "Master object-oriented programming in Python",
                "Work with files, APIs, and databases",
                "Build real-world projects from scratch",
                "Debug and test Python applications",
                "Understand Python best practices and design patterns",
            ],
            prerequisites=[],
            difficulty=DifficultyLevel.BEGINNER,
            estimated_duration_minutes=2400,
            status=ContentStatus.PUBLISHED,
            skill_tags=["Python", "Programming", "Backend", "Scripting"],
            module_count=6,
            lesson_count=24,
            enrollment_count=15420,
            rating_average=4.8,
            rating_count=3240,
            is_featured=True,
            is_free=True,
            author_id=admin.id,
            published_at=datetime(2024, 1, 15, tzinfo=timezone.utc),
        )
        db.add(python_course)
        courses["python"] = python_course

        # JavaScript Course
        js_course = Course(
            id=uuid4(),
            title="JavaScript: The Complete Guide",
            slug="javascript-complete-guide",
            description="Learn JavaScript from fundamentals to advanced concepts. Master the language that powers the modern web.",
            long_description="""## Master JavaScript

JavaScript is the most widely-used programming language, powering everything from interactive websites to server applications and mobile apps.

### What You'll Master
- JavaScript fundamentals and ES6+ features
- DOM manipulation and browser APIs
- Asynchronous programming and Promises
- Modern JavaScript patterns and best practices""",
            learning_objectives=[
                "Understand JavaScript fundamentals thoroughly",
                "Master DOM manipulation and events",
                "Work with async/await and Promises",
                "Build interactive web applications",
            ],
            prerequisites=["Basic HTML knowledge helpful but not required"],
            difficulty=DifficultyLevel.BEGINNER,
            estimated_duration_minutes=1800,
            status=ContentStatus.PUBLISHED,
            skill_tags=["JavaScript", "Web Development", "Frontend", "ES6"],
            module_count=5,
            lesson_count=20,
            enrollment_count=12100,
            rating_average=4.7,
            rating_count=2890,
            is_featured=True,
            is_free=True,
            author_id=admin.id,
            published_at=datetime(2024, 2, 1, tzinfo=timezone.utc),
        )
        db.add(js_course)
        courses["javascript"] = js_course

        # HTML & CSS Course
        web_course = Course(
            id=uuid4(),
            title="HTML & CSS: Build Beautiful Websites",
            slug="html-css-fundamentals",
            description="Learn to build stunning, responsive websites with HTML5 and CSS3. From semantic markup to modern layouts.",
            learning_objectives=[
                "Write semantic HTML5 markup",
                "Style pages with modern CSS3",
                "Build responsive layouts with Flexbox and Grid",
                "Create animations and transitions",
            ],
            prerequisites=[],
            difficulty=DifficultyLevel.BEGINNER,
            estimated_duration_minutes=1200,
            status=ContentStatus.PUBLISHED,
            skill_tags=["HTML", "CSS", "Web Design", "Responsive"],
            module_count=4,
            lesson_count=16,
            enrollment_count=18900,
            rating_average=4.9,
            rating_count=4100,
            is_featured=True,
            is_free=True,
            author_id=admin.id,
            published_at=datetime(2024, 1, 10, tzinfo=timezone.utc),
        )
        db.add(web_course)
        courses["htmlcss"] = web_course

        # ── Python Modules & Lessons ─────────────────────────
        python_modules = []
        module_data = [
            ("python-basics", "Getting Started with Python", "Python installation, syntax, variables, and your first program", [
                ("hello-world", "Your First Python Program", "beginner", """# Your First Python Program

Welcome to Python programming! In this lesson, you'll write your very first Python program and understand the basics of how Python works.

## What is Python?

Python is a high-level, interpreted programming language known for its readability and simplicity. Created by Guido van Rossum and first released in 1991, Python has grown to become one of the most popular programming languages in the world.

## Why Python?

- **Readable**: Python's syntax is clean and easy to understand
- **Versatile**: Used in web development, data science, AI, automation, and more
- **Large Community**: Millions of developers use Python; help is always available
- **Rich Ecosystem**: Thousands of libraries for almost any task

## Setting Up Python

### Installation
1. Visit [python.org](https://python.org)
2. Download the latest version for your OS
3. Run the installer (check "Add Python to PATH" on Windows)
4. Verify installation: open terminal and type `python --version`

### Your First Program

```python
print("Hello, World!")
```

This simple line does something amazing: it tells the computer to display text on the screen. The `print()` function is one of Python's built-in functions that outputs text to the console.

### Understanding the Code
- `print` is a function name
- `()` contains the arguments (what we want to print)
- `"Hello, World!"` is a string — a sequence of characters
- The quotes tell Python this is text, not code

## Variables

Variables are containers for storing data values. In Python, you create a variable by assigning a value to a name:

```python
name = "Alex"
age = 25
height = 1.75
is_student = True
```

### Variable Naming Rules
- Must start with a letter or underscore
- Can contain letters, numbers, and underscores
- Case-sensitive (`name` and `Name` are different)
- Cannot use Python keywords (like `print`, `if`, `for`)

```python
# Valid variable names
first_name = "Alice"
age_2 = 30
_total = 100

# Invalid variable names
# 2name = "Bob"      # Cannot start with number
# my-name = "Bob"    # Hyphens not allowed
# class = "CS101"    # 'class' is a keyword
```

## Comments

Comments help explain your code. Python ignores comments when running the program.

```python
# This is a single-line comment

# Comments can explain complex logic
result = 42  # The answer to everything

"""
This is a multi-line comment (docstring).
Useful for longer explanations.
"""
```

## Quick Check
1. What function prints text to the console?
2. What's the difference between `"Hello"` and `Hello` in Python?
3. Which of these is a valid variable name: `my-var`, `my_var`, `2var`?

## Practice Challenge
Write a Python program that:
1. Creates a variable with your name
2. Creates a variable with your age
3. Prints a greeting using both variables

```python
# Write your solution here
name = "Your Name"
age = 0
print(f"Hello, my name is {name} and I am {age} years old!")
```

> **Tip:** The `f` before the string creates an f-string, which lets you embed variables directly in the string using `{variable_name}`.
"""),
                ("python-types", "Data Types and Operators", "beginner", """# Data Types and Operators

Understanding data types and operators is fundamental to programming in Python.

## Python's Built-in Data Types

### Numeric Types

```python
# Integers - whole numbers
age = 25
year = 2024
negative = -10

# Floats - decimal numbers
price = 19.99
pi = 3.14159
temperature = -2.5

# Complex numbers (advanced)
z = 3 + 4j
```

### Strings
```python
# Strings can use single or double quotes
first_name = 'Alice'
last_name = "Smith"

# Multi-line strings
message = """This is a
multi-line string"""

# String operations
full_name = first_name + " " + last_name  # Concatenation
greeting = f"Hello, {full_name}!"  # f-strings
```

### Booleans
```python
is_active = True
is_complete = False
is_valid = 10 > 5  # True
```

### Lists, Tuples, and Dictionaries
```python
# Lists - ordered, mutable
fruits = ["apple", "banana", "orange"]
numbers = [1, 2, 3, 4, 5]

# Tuples - ordered, immutable
coordinates = (10, 20)
rgb = (255, 128, 0)

# Dictionaries - key-value pairs
person = {
    "name": "Alice",
    "age": 30,
    "city": "New York"
}
```

## Operators

### Arithmetic Operators
```python
a = 10
b = 3

print(a + b)   # 13 (addition)
print(a - b)   # 7  (subtraction)
print(a * b)   # 30 (multiplication)
print(a / b)   # 3.333... (division)
print(a // b)  # 3  (floor division)
print(a % b)   # 1  (modulus)
print(a ** b)  # 1000 (exponentiation)
```

### Comparison Operators
```python
x = 5
y = 10

print(x == y)  # False (equal to)
print(x != y)  # True  (not equal to)
print(x < y)   # True  (less than)
print(x > y)   # False (greater than)
print(x <= y)  # True  (less than or equal)
print(x >= y)  # False (greater than or equal)
```

### Logical Operators
```python
a = True
b = False

print(a and b)  # False
print(a or b)   # True
print(not a)    # False
```

## Type Conversion
```python
# Converting between types
num_str = "42"
num_int = int(num_str)    # 42
num_float = float(num_str) # 42.0

price = 19.99
price_int = int(price)    # 19 (truncates decimal)

# Checking types
print(type(42))           # <class 'int'>
print(type("hello"))      # <class 'str'>
print(isinstance(42, int)) # True
```

## Practice Challenge
Create a simple calculator that:
1. Stores two numbers in variables
2. Performs all arithmetic operations on them
3. Prints the results with descriptions

```python
num1 = 15
num2 = 4

# Write your solution
print(f"Addition: {num1 + num2}")
print(f"Subtraction: {num1 - num2}")
# ... continue for all operations
```
"""),
                ("control-flow", "Control Flow: Conditions", "beginner", """# Control Flow: Conditions

Control flow determines the order in which your code executes. Conditional statements let your program make decisions.

## if, elif, else Statements

```python
# Basic if statement
age = 18
if age >= 18:
    print("You are an adult")

# if-else statement
temperature = 25
if temperature > 30:
    print("It's hot outside!")
else:
    print("The weather is pleasant.")

# if-elif-else chain
score = 85
if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
elif score >= 60:
    grade = "D"
else:
    grade = "F"
print(f"Your grade is: {grade}")
```

## Comparison and Logic in Conditions
```python
# Multiple conditions with and/or
age = 25
has_license = True

if age >= 18 and has_license:
    print("You can drive")

# Nested conditions
is_weekend = True
weather = "sunny"

if is_weekend:
    if weather == "sunny":
        print("Let's go to the beach!")
    else:
        print("Let's watch a movie.")
```

## Match Statement (Python 3.10+)
```python
command = "start"

match command:
    case "start":
        print("Starting...")
    case "stop":
        print("Stopping...")
    case "pause":
        print("Pausing...")
    case _:
        print("Unknown command")
```

## Ternary Operator
```python
# One-line conditional
age = 20
status = "adult" if age >= 18 else "minor"
```

## Practice Challenge
Write a program that:
1. Takes a number input
2. Prints whether it's positive, negative, or zero
3. If positive, checks if it's even or odd
"""),
            ]),
            ("python-functions", "Functions and Scope", "Python functions, parameters, return values, and scope", [
                ("functions-intro", "Introduction to Functions", "beginner", """# Functions in Python

Functions are reusable blocks of code that perform specific tasks.

## Defining Functions

```python
def greet():
    print("Hello, World!")

# Calling the function
greet()  # Output: Hello, World!
```

## Parameters and Arguments

```python
# Function with parameters
def greet(name):
    print(f"Hello, {name}!")

greet("Alice")  # Hello, Alice!
greet("Bob")    # Hello, Bob!

# Multiple parameters
def introduce(name, age, city):
    print(f"I'm {name}, {age} years old from {city}.")

# Default parameters
def greet(name, greeting="Hello"):
    print(f"{greeting}, {name}!")

greet("Alice")              # Hello, Alice!
greet("Bob", greeting="Hi") # Hi, Bob!
```

## Return Values

```python
def add(a, b):
    return a + b

result = add(5, 3)  # result = 8

# Multiple return values (as tuple)
def min_max(numbers):
    return min(numbers), max(numbers)

low, high = min_max([1, 5, 3, 9, 2])
print(f"Min: {low}, Max: {high}")
```

## Scope

```python
# Global scope
global_var = "I'm global"

def my_function():
    # Local scope
    local_var = "I'm local"
    print(global_var)   # Accessible
    print(local_var)    # Accessible

# print(local_var)  # Error! Not accessible

# Modifying global variables
counter = 0

def increment():
    global counter
    counter += 1
```

## Practice
Write a function `calculate_bmi(weight_kg, height_m)` that returns the BMI and category.
"""),
                ("lambda-functions", "Lambda Functions", "intermediate", """# Lambda Functions

Lambda functions are small, anonymous functions defined with the `lambda` keyword.

## Syntax

```python
# Regular function
def square(x):
    return x ** 2

# Lambda equivalent
square = lambda x: x ** 2

print(square(5))  # 25
```

## Use with Built-in Functions

```python
# sort() with key
students = [
    {"name": "Alice", "score": 85},
    {"name": "Bob", "score": 92},
    {"name": "Charlie", "score": 78},
]
students.sort(key=lambda s: s["score"], reverse=True)

# filter() - keep elements that return True
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
evens = list(filter(lambda x: x % 2 == 0, numbers))

# map() - transform each element
squared = list(map(lambda x: x ** 2, numbers))
```

## Practice
Use lambda with `sorted()` to sort a list of words by their length.
"""),
            ]),
            ("python-data", "Data Structures", "Lists, dictionaries, sets, tuples, and comprehensions", [
                ("lists-tuples", "Lists and Tuples Deep Dive", "beginner", """# Lists and Tuples

## Lists
```python
# Creating lists
fruits = ["apple", "banana", "cherry"]
mixed = [1, "hello", 3.14, True]

# Accessing elements
print(fruits[0])      # apple
print(fruits[-1])     # cherry (last element)

# Slicing
print(fruits[0:2])    # ['apple', 'banana']
print(fruits[::2])    # ['apple', 'cherry'] (every 2nd)

# Modifying
fruits.append("orange")
fruits.insert(1, "grape")
fruits.remove("banana")
popped = fruits.pop()  # removes and returns last item
```

## List Methods
```python
numbers = [3, 1, 4, 1, 5, 9, 2]
numbers.sort()         # [1, 1, 2, 3, 4, 5, 9]
numbers.reverse()      # [9, 5, 4, 3, 2, 1, 1]
count = numbers.count(1)  # 2
index = numbers.index(9)  # 0 (after reverse)
```

## Tuples
```python
# Immutable sequences
coordinates = (10, 20)
rgb = (255, 128, 0)

# Tuple unpacking
x, y = coordinates
r, g, b = rgb
```

## Practice
Create a program that takes a list of numbers and returns the sum, average, min, and max.
"""),
                ("dicts-sets", "Dictionaries and Sets", "beginner", """# Dictionaries and Sets

## Dictionaries
```python
# Creating dictionaries
person = {"name": "Alice", "age": 30, "city": "New York"}
config = dict(host="localhost", port=5432)

# Accessing and modifying
print(person["name"])
person["email"] = "alice@example.com"
person["age"] = 31

# Safe access with .get()
print(person.get("phone", "Not found"))  # Not found

# Iterating
for key, value in person.items():
    print(f"{key}: {value}")
```

## Dictionary Comprehensions
```python
squares = {x: x**2 for x in range(6)}
# {0: 0, 1: 1, 2: 4, 3: 9, 4: 16, 5: 25}
```

## Sets
```python
# Unordered, unique elements
fruits = {"apple", "banana", "cherry", "apple"}
print(fruits)  # {'banana', 'cherry', 'apple'}

# Set operations
a = {1, 2, 3, 4}
b = {3, 4, 5, 6}
print(a | b)   # Union: {1, 2, 3, 4, 5, 6}
print(a & b)   # Intersection: {3, 4}
print(a - b)   # Difference: {1, 2}
```

## Practice
Create a function that finds the most frequent word in a sentence using a dictionary.
"""),
            ]),
            ("python-oop", "Object-Oriented Programming", "Classes, objects, inheritance, and design patterns", [
                ("classes-intro", "Classes and Objects", "intermediate", """# Classes and Objects

## Defining Classes

```python
class Dog:
    # Class attribute
    species = "Canis familiaris"

    # Constructor
    def __init__(self, name, age):
        self.name = name    # Instance attribute
        self.age = age

    # Instance method
    def bark(self):
        return f"{self.name} says woof!"

    def description(self):
        return f"{self.name} is {self.age} years old"

# Creating objects (instances)
buddy = Dog("Buddy", 5)
max = Dog("Max", 3)

print(buddy.bark())          # Buddy says woof!
print(buddy.description())   # Buddy is 5 years old
```

## Inheritance

```python
# Parent class
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        pass

# Child classes
class Cat(Animal):
    def speak(self):
        return f"{self.name} says meow!"

class Dog(Animal):
    def speak(self):
        return f"{self.name} says woof!"

# Using polymorphism
animals = [Cat("Whiskers"), Dog("Rex")]
for animal in animals:
    print(animal.speak())
```

## Special Methods (Dunder)

```python
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return f"Vector({self.x}, {self.y})"

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __len__(self):
        return 2

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
```

## Practice
Create a `BankAccount` class with deposit, withdraw, and balance methods.
"""),
            ]),
            ("python-projects", "Projects and Next Steps", "Apply everything you've learned in real projects", [
                ("final-project", "Capstone: Build a CLI Task Manager", "intermediate", """# Capstone Project: CLI Task Manager

Apply everything you've learned to build a command-line task manager.

## Requirements
1. Add, list, complete, and delete tasks
2. Save tasks to a JSON file
3. Support priority levels (high/medium/low)
4. Filter tasks by status and priority
5. Clean, well-documented code

## Starter Template

```python
import json
from datetime import datetime

class TaskManager:
    def __init__(self, filename="tasks.json"):
        self.filename = filename
        self.tasks = self.load_tasks()

    def load_tasks(self):
        try:
            with open(self.filename, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_tasks(self):
        with open(self.filename, "w") as f:
            json.dump(self.tasks, f, indent=2)

    def add_task(self, title, priority="medium"):
        task = {
            "id": len(self.tasks) + 1,
            "title": title,
            "priority": priority,
            "completed": False,
            "created_at": datetime.now().isoformat(),
        }
        self.tasks.append(task)
        self.save_tasks()

    def list_tasks(self, status=None, priority=None):
        filtered = self.tasks
        if status == "completed":
            filtered = [t for t in filtered if t["completed"]]
        elif status == "pending":
            filtered = [t for t in filtered if not t["completed"]]
        if priority:
            filtered = [t for t in filtered if t["priority"] == priority]
        return filtered

# Complete the implementation!
```

## Bonus Challenges
- Add due dates with overdue warnings
- Implement task categories
- Add a search function
- Create a web interface using Flask
"""),
            ]),
        ]

        for mod_idx, (mod_slug, mod_title, mod_desc, lessons_data) in enumerate(module_data):
            module = Module(
                course_id=python_course.id,
                title=mod_title,
                slug=mod_slug,
                description=mod_desc,
                display_order=mod_idx + 1,
                lesson_count=len(lessons_data),
            )
            db.add(module)

            for les_idx, (les_slug, les_title, les_diff, les_content) in enumerate(lessons_data):
                lesson = Lesson(
                    module_id=module.id,
                    title=les_title,
                    slug=les_slug,
                    description=f"Learn about {les_title.lower()} in Python",
                    content=les_content,
                    content_markdown=les_content,
                    learning_objectives=["Understand the core concepts", "Apply knowledge through practice", "Build confidence with hands-on exercises"],
                    difficulty=DifficultyLevel(les_diff),
                    estimated_duration_minutes=45,
                    display_order=les_idx + 1,
                    skill_tags=["Python"],
                    status=ContentStatus.PUBLISHED,
                    published_at=datetime.now(timezone.utc),
                )
                db.add(lesson)

                # Add exercises for each lesson
                exercise = Exercise(
                    lesson_id=lesson.id,
                    title=f"Practice: {les_title}",
                    description=f"Test your understanding of {les_title.lower()}",
                    instructions=f"Complete the following challenges related to {les_title.lower()}",
                    exercise_type=ExerciseType.CODE_COMPLETION,
                    difficulty=ExerciseDifficulty.EASY if les_diff == "beginner" else ExerciseDifficulty.MEDIUM,
                    starter_code="# Write your solution here\n",
                    solution_code="# Solutions vary\n",
                    test_code="# Test assertions\nassert True",
                    hints=[{"level": 1, "content": "Review the lesson material first"}, {"level": 2, "content": "Check the examples in the lesson"}],
                    skill_tags=["Python"],
                    points=15,
                )
                db.add(exercise)

        # ── Achievements ──────────────────────────────────────
        achievement_data = [
            ("python-starter", "Python Starter", "Complete your first Python lesson", "🐍", AchievementCategory.LEARNING, 50),
            ("code-warrior", "Code Warrior", "Complete 10 coding exercises", "⚔️", AchievementCategory.PRACTICE, 100),
            ("week-streak", "7-Day Streak", "Maintain a 7-day learning streak", "🔥", AchievementCategory.STREAK, 200),
            ("course-complete", "Course Graduate", "Complete your first course", "🎓", AchievementCategory.MILESTONE, 500),
            ("perfect-score", "Perfect Score", "Get 100% on an exercise", "⭐", AchievementCategory.PRACTICE, 75),
            ("early-bird", "Early Bird", "Complete 5 lessons before 9 AM", "🌅", AchievementCategory.SPECIAL, 150),
        ]
        for name, title, desc, icon, cat, xp in achievement_data:
            db.add(Achievement(
                name=title,
                description=desc,
                icon=icon,
                category=cat,
                xp_reward=xp,
                criteria={"type": name},
            ))

        # ── Feature Flags ─────────────────────────────────────
        flags = [
            ("enable_ai_features", "Enable AI-powered features", True),
            ("enable_sandbox", "Enable secure code sandbox", True),
            ("enable_registration", "Allow new user registration", True),
            ("enable_leaderboards", "Enable public leaderboards", True),
            ("enable_discussions", "Enable discussion forums", True),
        ]
        for name, desc, enabled in flags:
            db.add(FeatureFlag(name=name, description=desc, is_enabled=enabled))

        print("Seeding complete!")
        print(f"  Admin: admin@dsir.dev / Admin@123!")
        print(f"  Demo:  demo@dsir.dev  / Demo@123!")


if __name__ == "__main__":
    asyncio.run(seed())
