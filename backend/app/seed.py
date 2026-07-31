"""
Seed data for DSir platform — production-ready course content.
Run: python -m app.seed
"""

import asyncio
from app.database import async_session_factory, engine, Base
from app.models import (
    User, UserStats, Category, TechnologyStack, Course, Module,
    Lesson, Exercise, ContentStatus, DifficultyLevel,
    ExerciseType, ExerciseDifficulty, Achievement, FeatureFlag,
    AchievementCategory, Notification, NotificationType,
)
from app.utils.security import hash_password
from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import select

# ── LESSON CONTENT ── (embedded for deployment)
_LC = {
    "python": {
        "python-basics": {
            "hello-world": '# Your First Python Program\n\nWelcome to Python! In this lesson you\'ll write your first program and understand how Python works.\n\n## What is Python?\n\nPython is a high-level, interpreted programming language known for readability and simplicity. Created by Guido van Rossum in 1991, it has become one of the most popular languages worldwide.\n\n## Why Learn Python?\n- **Readable syntax** — clean and easy to understand\n- **Versatile** — web dev, data science, AI, automation, scripting\n- **Massive ecosystem** — thousands of libraries\n- **Great community** — millions of developers, abundant resources\n\n## Your First Program\n\n```python\nprint("Hello, World!")\n```\n\nThe `print()` function outputs text. `"Hello, World!"` is a string (text data).\n\n## Variables\n```python\nname = "Alex"\nage = 25\nheight = 1.75\nis_student = True\n```\n\nVariables store data. Python figures out the type automatically.\n\n## Variable Naming Rules\n- Start with a letter or underscore\n- Use letters, numbers, underscores only\n- Case-sensitive (`name` ≠ `Name`)\n- Don\'t use Python keywords (`print`, `if`, `for`, etc.)\n\n## Comments\n```python\n# This is a comment\nname = "Alice"  # Inline comment\n\n"""\nMulti-line\ncomment (docstring)\n"""\n```\n\n## Practice\nWrite a program that:\n1. Creates a variable with your name\n2. Creates a variable with your age  \n3. Prints: "Hello, my name is [name] and I am [age] years old"\n\n```python\nname = "Your Name"\nage = 0\nprint(f"Hello, my name is {name} and I am {age} years old!")\n```\n',
            "data-types": '# Data Types and Operators\n\n## Numeric Types\n```python\nage = 25           # int (integer)\nprice = 19.99      # float\ncomplex_num = 3+4j # complex\n```\n\n## Strings\n```python\nname = "Alice"\nmessage = \'Hello\'\nmultiline = """Line 1\nLine 2"""\n\n# f-strings (formatted strings)\ngreeting = f"Hello, {name}!"\n\n# String operations\nfull = "Hello" + " " + "World"  # concatenation\nprint(len("Hello"))  # 5\nprint("hello".upper())  # HELLO\n```\n\n## Booleans\n```python\nis_active = True\nis_valid = 10 > 5  # True\n```\n\n## Lists, Tuples, Dicts\n```python\nfruits = ["apple", "banana", "cherry"]  # list\npoint = (10, 20)                         # tuple\nperson = {"name": "Alice", "age": 30}    # dict\n```\n\n## Operators\n```python\n# Arithmetic\nprint(10 + 3)   # 13\nprint(10 - 3)   # 7\nprint(10 * 3)   # 30\nprint(10 / 3)   # 3.333...\nprint(10 // 3)  # 3 (floor division)\nprint(10 % 3)   # 1 (modulus)\nprint(10 ** 3)  # 1000 (power)\n\n# Comparison\nprint(5 == 5)   # True\nprint(5 != 3)   # True\nprint(5 > 3)    # True\n\n# Logical\nprint(True and False)  # False\nprint(True or False)   # True\nprint(not True)        # False\n```\n\n## Type Conversion\n```python\nnum = int("42")      # 42\ntext = str(100)      # "100"\npi = float("3.14")   # 3.14\n```\n\n## Practice\nCreate a calculator that stores two numbers and performs all arithmetic operations.\n',
            "control-flow": '# Control Flow\n\n## if, elif, else\n```python\nage = 18\nif age >= 18:\n    print("You can vote!")\nelif age >= 13:\n    print("You\'re a teenager.")\nelse:\n    print("You\'re a child.")\n\n# Multiple conditions\nscore = 85\nif score >= 90:\n    grade = "A"\nelif score >= 80:\n    grade = "B"\nelif score >= 70:\n    grade = "C"\nelse:\n    grade = "F"\n```\n\n## Loops\n```python\n# for loop\nfor i in range(5):\n    print(i)  # 0, 1, 2, 3, 4\n\nfruits = ["apple", "banana", "cherry"]\nfor fruit in fruits:\n    print(fruit)\n\n# while loop\ncount = 0\nwhile count < 5:\n    print(count)\n    count += 1\n```\n\n## break and continue\n```python\nfor i in range(10):\n    if i == 5:\n        break      # exits loop\n    if i % 2 == 0:\n        continue   # skips rest of iteration\n    print(i)       # prints 1, 3\n```\n\n## Ternary Expression\n```python\nage = 20\nstatus = "adult" if age >= 18 else "minor"\n```\n\n## Practice\nWrite a FizzBuzz program: print 1-50, but print "Fizz" for multiples of 3, "Buzz" for multiples of 5, and "FizzBuzz" for multiples of both.\n',
        },
        "functions": {
            "functions-basics": '# Functions\n\nFunctions are reusable blocks of code.\n\n## Defining and Calling\n```python\ndef greet():\n    print("Hello!")\n\ngreet()  # Hello!\n```\n\n## Parameters & Arguments\n```python\ndef greet(name, greeting="Hello"):\n    print(f"{greeting}, {name}!")\n\ngreet("Alice")              # Hello, Alice!\ngreet("Bob", "Hi")          # Hi, Bob!\n```\n\n## Return Values\n```python\ndef add(a, b):\n    return a + b\n\nresult = add(5, 3)  # 8\n\ndef get_stats(numbers):\n    return min(numbers), max(numbers), sum(numbers)/len(numbers)\n\nlow, high, avg = get_stats([1, 2, 3, 4, 5])\n```\n\n## *args and **kwargs\n```python\ndef sum_all(*args):\n    return sum(args)\n\nprint(sum_all(1, 2, 3, 4, 5))  # 15\n\ndef print_info(**kwargs):\n    for key, value in kwargs.items():\n        print(f"{key}: {value}")\n\nprint_info(name="Alice", age=30)\n```\n\n## Scope\n```python\nglobal_var = "I\'m global"\n\ndef my_func():\n    local_var = "I\'m local"\n    print(global_var)  # accessible\n    print(local_var)   # accessible\n\n# print(local_var)  # ERROR - not accessible\n\ncounter = 0\ndef increment():\n    global counter\n    counter += 1\n```\n\n## Practice\nWrite a `calculate_bmi(weight_kg, height_m)` function that returns BMI value and category.\n',
            "lambda-map-filter": '# Lambda, Map & Filter\n\n## Lambda Functions\n```python\nsquare = lambda x: x ** 2\nprint(square(5))  # 25\n\nadd = lambda a, b: a + b\nprint(add(3, 4))  # 7\n```\n\n## map()\n```python\nnumbers = [1, 2, 3, 4, 5]\nsquared = list(map(lambda x: x**2, numbers))\n# [1, 4, 9, 16, 25]\n\nnames = ["alice", "bob", "charlie"]\ncapitalized = list(map(str.title, names))\n# [\'Alice\', \'Bob\', \'Charlie\']\n```\n\n## filter()\n```python\nnumbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]\nevens = list(filter(lambda x: x % 2 == 0, numbers))\n# [2, 4, 6, 8, 10]\n\nwords = ["cat", "elephant", "dog", "giraffe"]\nlong_words = list(filter(lambda w: len(w) > 3, words))\n# [\'elephant\', \'giraffe\']\n```\n\n## sorted() with key\n```python\nstudents = [{"name": "Alice", "score": 85}, {"name": "Bob", "score": 92}]\nranked = sorted(students, key=lambda s: s["score"], reverse=True)\n```\n\n## Practice\nUse lambda with filter to find all palindromes in a list of words.\n',
        },
        "lists-tuples": {
            "lists-tuples": '# Lists and Tuples\n\n## Lists\n```python\nfruits = ["apple", "banana", "cherry"]\nmixed = [1, "hello", 3.14, True]\n\n# Accessing\nprint(fruits[0])     # apple  \nprint(fruits[-1])    # cherry (last)\n\n# Slicing\nprint(fruits[0:2])   # [\'apple\', \'banana\']\nprint(fruits[::2])   # every other\n\n# Modifying\nfruits.append("orange")\nfruits.insert(1, "grape")\nfruits.remove("banana")\npopped = fruits.pop()  # removes last\n\n# List operations\nnumbers = [3, 1, 4, 1, 5, 9, 2]\nnumbers.sort()          # [1, 1, 2, 3, 4, 5, 9]\nprint(len(numbers))     # 7\nprint(sum(numbers))     # 25\n```\n\n## List Comprehensions\n```python\nsquares = [x**2 for x in range(10)]\n# [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]\n\nevens = [x for x in range(20) if x % 2 == 0]\n```\n\n## Tuples (Immutable)\n```python\ncoords = (10, 20)\nrgb = (255, 128, 0)\nx, y = coords  # unpacking\n```\n\n## Practice\nWrite a function that takes a list of numbers and returns min, max, sum, and average.\n',
            "dicts-sets": '# Dictionaries & Sets\n\n## Dictionaries\n```python\nperson = {"name": "Alice", "age": 30, "city": "NYC"}\n\n# Access\nprint(person["name"])\nprint(person.get("phone", "N/A"))  # safe access\n\n# Modify\nperson["email"] = "alice@example.com"\nperson["age"] = 31\ndel person["city"]\n\n# Iterating\nfor key, value in person.items():\n    print(f"{key}: {value}")\n\n# Dict comprehension\nsquares = {x: x**2 for x in range(6)}\n```\n\n## Sets\n```python\nfruits = {"apple", "banana", "cherry", "apple"}  # duplicates removed\n# {\'banana\', \'cherry\', \'apple\'}\n\na = {1, 2, 3, 4}\nb = {3, 4, 5, 6}\nprint(a | b)   # Union: {1, 2, 3, 4, 5, 6}\nprint(a & b)   # Intersection: {3, 4}\nprint(a - b)   # Difference: {1, 2}\n\n# Useful for deduplication\nnumbers = [1, 2, 2, 3, 3, 3, 4]\nunique = list(set(numbers))  # [1, 2, 3, 4]\n```\n\n## Practice\nCreate a word frequency counter using a dictionary.\n',
        },
        "oop-basics": {
            "classes-objects": '# Object-Oriented Programming\n\n## Defining Classes\n```python\nclass Dog:\n    species = "Canis familiaris"  # class attribute\n\n    def __init__(self, name, age):\n        self.name = name  # instance attribute\n        self.age = age\n\n    def bark(self):\n        return f"{self.name} says woof!"\n\nbuddy = Dog("Buddy", 5)\nprint(buddy.bark())  # Buddy says woof!\n```\n\n## Inheritance\n```python\nclass Animal:\n    def __init__(self, name):\n        self.name = name\n    def speak(self):\n        pass\n\nclass Cat(Animal):\n    def speak(self):\n        return f"{self.name} says meow!"\n\nclass Dog(Animal):\n    def speak(self):\n        return f"{self.name} says woof!"\n```\n\n## Special Methods\n```python\nclass Vector:\n    def __init__(self, x, y):\n        self.x, self.y = x, y\n    def __str__(self):\n        return f"Vector({self.x}, {self.y})"\n    def __add__(self, other):\n        return Vector(self.x + other.x, self.y + other.y)\n    def __eq__(self, other):\n        return self.x == other.x and self.y == other.y\n```\n\n## Properties\n```python\nclass Circle:\n    def __init__(self, radius):\n        self._radius = radius\n\n    @property\n    def area(self):\n        return 3.14159 * self._radius ** 2\n\n    @property\n    def radius(self):\n        return self._radius\n\n    @radius.setter\n    def radius(self, value):\n        if value < 0:\n            raise ValueError("Radius cannot be negative")\n        self._radius = value\n```\n\n## Practice\nCreate a `BankAccount` class with deposit, withdraw, transfer methods and proper validation.\n',
            "inheritance-polymorphism": '# Inheritance & Polymorphism\n\n## Multiple Inheritance\n```python\nclass Flyer:\n    def fly(self):\n        return "Flying"\n\nclass Swimmer:\n    def swim(self):\n        return "Swimming"\n\nclass Duck(Flyer, Swimmer):\n    def quack(self):\n        return "Quack!"\n```\n\n## Abstract Base Classes\n```python\nfrom abc import ABC, abstractmethod\n\nclass Shape(ABC):\n    @abstractmethod\n    def area(self):\n        pass\n\n    @abstractmethod\n    def perimeter(self):\n        pass\n\nclass Rectangle(Shape):\n    def __init__(self, w, h):\n        self.w, self.h = w, h\n\n    def area(self):\n        return self.w * self.h\n\n    def perimeter(self):\n        return 2 * (self.w + self.h)\n```\n\n## Class Methods & Static Methods\n```python\nclass Date:\n    def __init__(self, year, month, day):\n        self.year, self.month, self.day = year, month, day\n\n    @classmethod\n    def from_string(cls, date_str):\n        year, month, day = map(int, date_str.split("-"))\n        return cls(year, month, day)\n\n    @staticmethod\n    def is_valid_date(year, month, day):\n        return 1 <= month <= 12 and 1 <= day <= 31\n\nd = Date.from_string("2024-01-15")\n```\n\n## Practice\nDesign a payment system with abstract `PaymentMethod` and concrete `CreditCard`, `PayPal`, `Crypto` classes.\n',
        },
        "advanced-python": {
            "file-io": '# File Handling\n\n## Reading Files\n```python\n# Read entire file\nwith open("data.txt", "r") as f:\n    content = f.read()\n\n# Read line by line\nwith open("data.txt", "r") as f:\n    for line in f:\n        print(line.strip())\n\n# Read lines to list\nwith open("data.txt", "r") as f:\n    lines = f.readlines()\n```\n\n## Writing Files\n```python\nwith open("output.txt", "w") as f:\n    f.write("Hello, World!\\n")\n    f.write("Line 2\\n")\n\n# Append mode\nwith open("log.txt", "a") as f:\n    f.write("New log entry\\n")\n```\n\n## JSON\n```python\nimport json\n\ndata = {"name": "Alice", "age": 30}\n\n# Write JSON\nwith open("data.json", "w") as f:\n    json.dump(data, f, indent=2)\n\n# Read JSON\nwith open("data.json", "r") as f:\n    loaded = json.load(f)\n```\n\n## Error Handling\n```python\ntry:\n    num = int(input("Enter a number: "))\n    result = 100 / num\nexcept ValueError:\n    print("That\'s not a number!")\nexcept ZeroDivisionError:\n    print("Cannot divide by zero!")\nexcept Exception as e:\n    print(f"Unexpected error: {e}")\nelse:\n    print(f"Result: {result}")\nfinally:\n    print("Done!")\n```\n\n## Practice\nBuild a program that reads a CSV file of student grades and calculates statistics.\n',
            "modules-packages": '# Modules & Packages\n\n## Creating Modules\n```python\n# my_math.py\ndef add(a, b): return a + b\ndef subtract(a, b): return a - b\nPI = 3.14159\n```\n\n```python\n# main.py\nimport my_math\nprint(my_math.add(5, 3))\n\nfrom my_math import add, PI\nprint(add(5, 3))\n\nimport my_math as m\nprint(m.PI)\n```\n\n## Packages\n```\nmypackage/\n    __init__.py\n    utils.py\n    models.py\n```\n\n```python\nfrom mypackage import utils\nfrom mypackage.utils import helper_function\n```\n\n## Standard Library Highlights\n```python\nimport os         # file system operations\nimport sys        # system parameters\nimport datetime   # dates and times\nimport random     # random numbers\nimport re         # regular expressions\nimport math       # math functions\nimport itertools  # iteration tools\nimport collections  # specialized containers\n```\n\n## Practice\nCreate a Python package with utility functions for string manipulation, file handling, and math operations.\n',
        },
        "projects": {
            "cli-task-manager": '# Capstone Project: CLI Task Manager\n\nBuild a complete command-line task manager to apply everything you\'ve learned.\n\n## Core Requirements\n1. Add, list, complete, and delete tasks\n2. Priority levels (high/medium/low)\n3. Persist tasks to JSON file\n4. Filter by status and priority\n5. Due dates with overdue warnings\n\n## Starter Code\n```python\nimport json\nfrom datetime import datetime, timedelta\n\nclass TaskManager:\n    def __init__(self, filename="tasks.json"):\n        self.filename = filename\n        self.tasks = self.load()\n\n    def load(self):\n        try:\n            with open(self.filename) as f:\n                return json.load(f)\n        except (FileNotFoundError, json.JSONDecodeError):\n            return []\n\n    def save(self):\n        with open(self.filename, "w") as f:\n            json.dump(self.tasks, f, indent=2)\n\n    def add(self, title, priority="medium", due_date=None):\n        # Implement task creation\n        pass\n\n    def list_tasks(self, status=None, priority=None):\n        # Implement filtering\n        pass\n\n    def complete(self, task_id):\n        # Implement completion\n        pass\n\n    def delete(self, task_id):\n        # Implement deletion\n        pass\n```\n\n## Bonus Features\n- Categories/tags for tasks\n- Search functionality  \n- Export to CSV\n- Color-coded terminal output\n- Task statistics dashboard\n',
        },
    },
        "strings": {
            "strings-intro": "String content from handbook - see lesson.",
        },
        "control-flow": {
            "conditionals": "Conditional content from handbook - see lesson.",
            "loops": "Loops content from handbook - see lesson.",
        },
        "file-io": {
            "file-handling": "File I/O content from handbook - see lesson.",
        },
        "oop-advanced": {
            "inheritance": "Inheritance content from handbook - see lesson.",
        },

            "dicts-sets": {
            "dicts-master": "Dictionaries & Sets — key-value pairs, dict methods, set operations. See our comprehensive handbook-style lesson.",
        },
"javascript": {
        "js-basics": {
            "js-intro": '# JavaScript Fundamentals\n\nJavaScript powers the interactive web. It runs in every browser and on servers via Node.js.\n\n## Variables\n```javascript\n// Modern approach (ES6+)\nlet name = "Alice";\nconst age = 30;  // cannot be reassigned\nvar oldWay = "avoid this";  // legacy\n\n// Dynamic typing\nlet value = 42;\nvalue = "now a string";  // valid!\n```\n\n## Data Types\n```javascript\n// Primitives\nlet str = "Hello";           // string\nlet num = 42;                // number\nlet bool = true;             // boolean\nlet nothing = null;          // null\nlet notDefined = undefined;  // undefined\nlet unique = Symbol("id");   // symbol\n\n// Reference\nlet arr = [1, 2, 3];         // array\nlet obj = { name: "Alice" }; // object\n```\n\n## Strings\n```javascript\nlet name = "Alice";\nconsole.log(`Hello, ${name}!`);  // template literal\nconsole.log(name.length);         // 5\nconsole.log(name.toUpperCase());  // ALICE\nconsole.log(name.includes("li")); // true\n```\n\n## Operators\n```javascript\n// Arithmetic: + - * / % **\n// Comparison: == === != !== > < >= <=\n// Logical: && || !\n\n// Strict equality (preferred)\nconsole.log(5 === "5");  // false\nconsole.log(5 == "5");   // true (type coercion)\n```\n\n## Practice\nWrite a program that declares variables of different types, performs operations, and logs results.\n',
            "js-arrays-objects": '# Arrays & Objects\n\n## Arrays\n```javascript\nconst fruits = ["apple", "banana", "cherry"];\n\n// Methods\nfruits.push("orange");        // add to end\nfruits.pop();                 // remove from end\nfruits.unshift("grape");      // add to start\nfruits.shift();               // remove from start\n\n// Iteration\nfruits.forEach(f => console.log(f));\n\nconst upper = fruits.map(f => f.toUpperCase());\nconst filtered = fruits.filter(f => f.length > 5);\nconst found = fruits.find(f => f.startsWith("a"));\n\n// Spread\nconst combined = [...fruits, "mango", "kiwi"];\n```\n\n## Objects\n```javascript\nconst person = {\n    name: "Alice",\n    age: 30,\n    greet() {\n        console.log(`Hi, I\'m ${this.name}`);\n    }\n};\n\n// Access\nconsole.log(person.name);\nconsole.log(person["age"]);\n\n// Destructuring\nconst { name, age } = person;\n\n// Spread\nconst updated = { ...person, age: 31 };\n\n// Object methods\nconsole.log(Object.keys(person));\nconsole.log(Object.values(person));\nconsole.log(Object.entries(person));\n```\n\n## Practice\nWrite functions that filter an array of objects, map them to new values, and destructure the results.\n',
        },
        "js-functions": {
            "js-functions-deep": '# JavaScript Functions\n\n## Function Declarations\n```javascript\nfunction greet(name) {\n    return `Hello, ${name}!`;\n}\n\n// Arrow functions (ES6+)\nconst greetArrow = (name) => `Hello, ${name}!`;\n\n// Default parameters\nfunction greet(name = "Guest") {\n    return `Hello, ${name}!`;\n}\n```\n\n## Callbacks\n```javascript\nfunction processUser(name, callback) {\n    const greeting = `Hello, ${name}`;\n    callback(greeting);\n}\n\nprocessUser("Alice", (msg) => console.log(msg));\n```\n\n## Closures\n```javascript\nfunction createCounter() {\n    let count = 0;\n    return {\n        increment: () => ++count,\n        getValue: () => count,\n    };\n}\n\nconst counter = createCounter();\ncounter.increment(); // 1\ncounter.increment(); // 2\n```\n\n## this Keyword\n```javascript\nconst user = {\n    name: "Alice",\n    greet() { console.log(`Hi, ${this.name}`); },\n    greetArrow: () => console.log(`Hi, ${this.name}`), // BUG: \'this\' is window\n};\n```\n\n## Practice\nBuild a debounce function that limits how often a function can fire.\n',
            "js-es6": '# Modern JavaScript\n\n## Destructuring\n```javascript\nconst [first, second, ...rest] = [1, 2, 3, 4, 5];\nconst { name, age, ...other } = { name: "A", age: 30, city: "NYC" };\n```\n\n## Modules\n```javascript\n// math.js\nexport const add = (a, b) => a + b;\nexport default class Calculator { }\n\n// main.js\nimport Calculator, { add } from \'./math.js\';\n```\n\n## Optional Chaining & Nullish Coalescing\n```javascript\nconst city = user?.address?.city ?? "Unknown";\n```\n\n## Classes\n```javascript\nclass Animal {\n    constructor(name) { this.name = name; }\n    speak() { console.log(`${this.name} makes a sound.`); }\n}\n\nclass Dog extends Animal {\n    speak() { console.log(`${this.name} barks.`); }\n}\n```\n\n## Map & Set\n```javascript\nconst map = new Map();\nmap.set("key", "value");\n\nconst set = new Set([1, 2, 2, 3]); // {1, 2, 3}\n```\n\n## Practice\nWrite a module that exports utility functions and import them in another file.\n',
        },
        "js-dom": {
            "dom-manipulation": '# DOM Manipulation\n\nThe DOM (Document Object Model) represents your HTML as a tree of objects.\n\n## Selecting Elements\n```javascript\nconst title = document.getElementById("title");\nconst buttons = document.getElementsByClassName("btn");\nconst paragraphs = document.getElementsByTagName("p");\n\n// Modern approach\nconst card = document.querySelector(".card");\nconst allCards = document.querySelectorAll(".card");\n```\n\n## Modifying Elements\n```javascript\nconst el = document.querySelector(".message");\nel.textContent = "New text";\nel.innerHTML = "<strong>Bold text</strong>";\nel.classList.add("active");\nel.classList.toggle("hidden");\nel.setAttribute("data-id", "123");\nel.style.color = "blue";\n```\n\n## Creating Elements\n```javascript\nconst div = document.createElement("div");\ndiv.className = "card";\ndiv.innerHTML = "<h2>Title</h2><p>Content</p>";\ndocument.body.appendChild(div);\n\n// Modern approach\ndiv.insertAdjacentHTML("beforeend", "<p>More content</p>");\n```\n\n## Events\n```javascript\nconst btn = document.querySelector("button");\nbtn.addEventListener("click", (e) => {\n    console.log("Clicked!", e.target);\n});\n\n// Event delegation\ndocument.querySelector(".list").addEventListener("click", (e) => {\n    if (e.target.matches(".item")) {\n        console.log("Item clicked:", e.target.textContent);\n    }\n});\n```\n\n## Practice\nBuild an interactive to-do list with add, complete, and delete functionality.\n',
            "events-forms": '# Events & Forms\n\n## Common Events\n```javascript\n// Mouse\nelement.addEventListener("click", handler);\nelement.addEventListener("dblclick", handler);\nelement.addEventListener("mouseenter", handler);\n\n// Keyboard\ndocument.addEventListener("keydown", (e) => {\n    if (e.key === "Escape") closeModal();\n});\n\n// Form\nform.addEventListener("submit", (e) => {\n    e.preventDefault();\n    // handle submission\n});\n```\n\n## Form Handling\n```javascript\nconst form = document.querySelector("form");\nform.addEventListener("submit", async (e) => {\n    e.preventDefault();\n\n    const formData = new FormData(form);\n    const data = Object.fromEntries(formData);\n\n    // Validate\n    if (!data.email.includes("@")) {\n        showError("Invalid email");\n        return;\n    }\n\n    // Submit\n    const response = await fetch("/api/submit", {\n        method: "POST",\n        headers: { "Content-Type": "application/json" },\n        body: JSON.stringify(data),\n    });\n});\n```\n\n## Form Validation\n```javascript\nfunction validateForm(data) {\n    const errors = {};\n\n    if (!data.name?.trim()) errors.name = "Name is required";\n    if (!data.email?.includes("@")) errors.email = "Invalid email";\n    if (data.password?.length < 8) errors.password = "Min 8 characters";\n\n    return Object.keys(errors).length ? errors : null;\n}\n```\n\n## Practice\nBuild a registration form with client-side validation and submission handling.\n',
        },
        "js-async": {
            "promises-async": '# Asynchronous JavaScript\n\n## Promises\n```javascript\nconst promise = new Promise((resolve, reject) => {\n    setTimeout(() => resolve("Done!"), 1000);\n});\n\npromise\n    .then(result => console.log(result))\n    .catch(error => console.error(error))\n    .finally(() => console.log("Cleanup"));\n```\n\n## Async/Await\n```javascript\nasync function fetchUser(id) {\n    try {\n        const response = await fetch(`/api/users/${id}`);\n        if (!response.ok) throw new Error("Not found");\n        const user = await response.json();\n        return user;\n    } catch (error) {\n        console.error("Failed to fetch user:", error);\n        throw error;\n    }\n}\n```\n\n## Fetch API\n```javascript\n// GET\nconst users = await fetch("/api/users").then(r => r.json());\n\n// POST\nconst newUser = await fetch("/api/users", {\n    method: "POST",\n    headers: { "Content-Type": "application/json" },\n    body: JSON.stringify({ name: "Alice" }),\n}).then(r => r.json());\n\n// Error handling\ntry {\n    const res = await fetch(url);\n    if (!res.ok) throw new Error(`HTTP ${res.status}`);\n    return await res.json();\n} catch (err) {\n    // handle network error or HTTP error\n}\n```\n\n## Parallel Execution\n```javascript\n// Run in parallel\nconst [users, posts] = await Promise.all([\n    fetch("/api/users").then(r => r.json()),\n    fetch("/api/posts").then(r => r.json()),\n]);\n```\n\n## Practice\nBuild an app that fetches data from an API with loading, error, and empty states.\n',
        },
        "js-projects": {
            "js-weather-app": '# Capstone: Weather Dashboard\n\nBuild a full-featured weather dashboard using everything you\'ve learned.\n\n## Requirements\n1. Search for any city\n2. Display current weather (temp, humidity, wind, conditions)\n3. Show 5-day forecast\n4. Save favorite cities (localStorage)\n5. Responsive design\n6. Loading and error states\n\n## API Setup\n```javascript\nconst API_KEY = "your_key_here";\nconst BASE_URL = "https://api.openweathermap.org/data/2.5";\n\nasync function getWeather(city) {\n    const res = await fetch(\n        `${BASE_URL}/weather?q=${city}&appid=${API_KEY}&units=metric`\n    );\n    if (!res.ok) throw new Error("City not found");\n    return res.json();\n}\n```\n\n## Core Features\n- Debounced search input\n- Temperature unit toggle (°C/°F)\n- Weather icons and descriptions\n- Local storage for favorites\n- Recent searches\n\n## Architecture\n```\nsrc/\n  components/\n    SearchBar.js\n    CurrentWeather.js\n    Forecast.js\n    Favorites.js\n  utils/\n    api.js\n    storage.js\n    formatters.js\n  app.js\n  styles.css\n```\n',
        },
    },
    "htmlcss": {
        "html-basics": {
            "html-intro": '# Introduction to HTML\n\nHTML (HyperText Markup Language) is the foundation of the web. Every website uses HTML to structure content.\n\n## What is HTML?\nHTML is a markup language that tells browsers how to structure web content. It uses **tags** to define elements like headings, paragraphs, images, and links.\n\n## Basic HTML Document\n```html\n<!DOCTYPE html>\n<html lang="en">\n<head>\n    <meta charset="UTF-8">\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n    <title>My First Page</title>\n</head>\n<body>\n    <h1>Hello, World!</h1>\n    <p>This is my first web page.</p>\n</body>\n</html>\n```\n\n## Key Concepts\n- `<!DOCTYPE html>` — declares HTML5 document\n- `<html>` — root element\n- `<head>` — metadata (title, styles, scripts)\n- `<body>` — visible content\n\n## Text Elements\n```html\n<h1>Main Heading</h1>\n<h2>Subheading</h2>\n<h3>Section Heading</h3>\n\n<p>This is a paragraph of text.</p>\n\n<strong>Bold text</strong>\n<em>Italic text</em>\n<mark>Highlighted text</mark>\n\n<br>  <!-- line break -->\n<hr>  <!-- horizontal rule -->\n```\n\n## Links & Images\n```html\n<a href="https://example.com">Visit Example</a>\n<a href="mailto:hello@example.com">Send Email</a>\n\n<img src="photo.jpg" alt="A beautiful sunset" width="400">\n```\n\n## Practice\nCreate an HTML page with a title, heading, paragraph, image, and link.\n',
            "html-semantics": '# Semantic HTML & Forms\n\n## Semantic Elements\nReplace generic `<div>` with meaningful elements:\n```html\n<header>    <!-- page/section header -->\n<nav>       <!-- navigation links -->\n<main>      <!-- main content -->\n<article>   <!-- self-contained content -->\n<section>   <!-- thematic grouping -->\n<aside>     <!-- sidebar content -->\n<footer>    <!-- page/section footer -->\n```\n\n## Lists\n```html\n<ul>\n    <li>Unordered item 1</li>\n    <li>Unordered item 2</li>\n</ul>\n\n<ol>\n    <li>First step</li>\n    <li>Second step</li>\n</ol>\n```\n\n## Tables\n```html\n<table>\n    <thead>\n        <tr><th>Name</th><th>Age</th></tr>\n    </thead>\n    <tbody>\n        <tr><td>Alice</td><td>30</td></tr>\n        <tr><td>Bob</td><td>25</td></tr>\n    </tbody>\n</table>\n```\n\n## Forms\n```html\n<form action="/submit" method="POST">\n    <label for="name">Name:</label>\n    <input type="text" id="name" name="name" required>\n\n    <label for="email">Email:</label>\n    <input type="email" id="email" name="email">\n\n    <label for="message">Message:</label>\n    <textarea id="message" name="message" rows="4"></textarea>\n\n    <label for="plan">Plan:</label>\n    <select id="plan" name="plan">\n        <option value="basic">Basic</option>\n        <option value="pro">Pro</option>\n    </select>\n\n    <button type="submit">Send</button>\n</form>\n```\n\n## Input Types\n```html\n<input type="text">\n<input type="email">\n<input type="password">\n<input type="number" min="0" max="100">\n<input type="date">\n<input type="checkbox">\n<input type="radio" name="group">\n<input type="file">\n<input type="color">\n```\n\n## Practice\nBuild a contact form with name, email, subject dropdown, message textarea, and submit button.\n',
        },
        "css-basics": {
            "css-intro": '# CSS Fundamentals\n\nCSS (Cascading Style Sheets) controls how HTML elements look.\n\n## Adding CSS\n```html\n<!-- External stylesheet (recommended) -->\n<link rel="stylesheet" href="styles.css">\n\n<!-- Internal styles -->\n<style>\n    h1 { color: blue; }\n</style>\n\n<!-- Inline (avoid for production) -->\n<p style="color: red;">Text</p>\n```\n\n## Selectors\n```css\n/* Element selector */\np { color: #333; }\n\n/* Class selector */\n.highlight { background: yellow; }\n\n/* ID selector (avoid for styling) */\n#header { height: 60px; }\n\n/* Descendant */\narticle p { line-height: 1.6; }\n\n/* Multiple selectors */\nh1, h2, h3 { font-family: sans-serif; }\n```\n\n## Colors\n```css\n.text {\n    color: #4c6ef5;        /* hex */\n    color: rgb(76, 110, 245); /* rgb */\n    color: rgba(76, 110, 245, 0.5); /* with opacity */\n    background: linear-gradient(to right, #4c6ef5, #748ffc);\n}\n```\n\n## Typography\n```css\nbody {\n    font-family: \'Inter\', sans-serif;\n    font-size: 16px;\n    line-height: 1.6;\n    font-weight: 400;\n    text-align: left;\n}\n```\n\n## Box Model\n```css\n.box {\n    width: 300px;\n    padding: 20px;\n    border: 2px solid #ddd;\n    margin: 10px;\n    border-radius: 8px;\n}\n```\n\n## Practice\nStyle a blog post with proper typography, colors, spacing, and a card component.\n',
            "css-layout": '# Flexbox & Grid\n\n## Flexbox\n```css\n.container {\n    display: flex;\n    justify-content: space-between;\n    align-items: center;\n    gap: 16px;\n    flex-wrap: wrap;\n}\n\n.item {\n    flex: 1;  /* grow equally */\n}\n\n.item-wide {\n    flex: 2;  /* grow twice as much */\n}\n```\n\n## Common Flexbox Patterns\n```css\n/* Center content */\n.center { display: flex; justify-content: center; align-items: center; }\n\n/* Navbar */\nnav { display: flex; justify-content: space-between; align-items: center; }\n\n/* Card grid */\n.cards { display: flex; flex-wrap: wrap; gap: 20px; }\n.cards > * { flex: 1 1 300px; }\n```\n\n## CSS Grid\n```css\n.grid {\n    display: grid;\n    grid-template-columns: repeat(3, 1fr);\n    gap: 20px;\n}\n\n/* Responsive grid */\n.responsive-grid {\n    display: grid;\n    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));\n    gap: 20px;\n}\n\n/* Grid areas */\n.layout {\n    display: grid;\n    grid-template-areas:\n        "header header"\n        "sidebar main"\n        "footer footer";\n    grid-template-columns: 250px 1fr;\n}\n```\n\n## Practice\nBuild a responsive page layout with header, sidebar, main content, and footer using Grid.\n',
        },
        "responsive-design": {
            "responsive-basics": '# Responsive Web Design\n\n## Viewport Meta Tag\n```html\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n```\n\n## Media Queries\n```css\n/* Mobile first approach */\n.card { padding: 16px; }\n\n/* Tablet */\n@media (min-width: 768px) {\n    .card { padding: 24px; }\n}\n\n/* Desktop */\n@media (min-width: 1024px) {\n    .card { padding: 32px; }\n    .grid { grid-template-columns: repeat(3, 1fr); }\n}\n```\n\n## Fluid Typography\n```css\nh1 { font-size: clamp(1.5rem, 5vw, 3rem); }\n```\n\n## Responsive Images\n```css\nimg {\n    max-width: 100%;\n    height: auto;\n}\n\n/* Art direction */\n<picture>\n    <source media="(min-width: 768px)" srcset="hero-lg.jpg">\n    <img src="hero-sm.jpg" alt="Hero">\n</picture>\n```\n\n## Mobile-First Principles\n1. Start with mobile layout\n2. Add complexity at breakpoints\n3. Use relative units (%, rem, vw)\n4. Test on real devices\n\n## Practice\nBuild a responsive navigation that collapses to hamburger menu on mobile.\n',
        },
        "css-advanced": {
            "animations": '# Animations & Transitions\n\n## Transitions\n```css\n.button {\n    background: #4c6ef5;\n    transition: background 0.3s ease, transform 0.2s;\n}\n\n.button:hover {\n    background: #4263eb;\n    transform: translateY(-2px);\n}\n```\n\n## Keyframe Animations\n```css\n@keyframes fadeIn {\n    from { opacity: 0; transform: translateY(10px); }\n    to { opacity: 1; transform: translateY(0); }\n}\n\n.card { animation: fadeIn 0.5s ease-out; }\n\n@keyframes pulse {\n    0%, 100% { transform: scale(1); }\n    50% { transform: scale(1.05); }\n}\n\n.icon { animation: pulse 2s infinite; }\n```\n\n## Transform\n```css\n.element:hover {\n    transform: scale(1.1) rotate(5deg) translateX(10px);\n}\n```\n\n## CSS Variables\n```css\n:root {\n    --brand: #4c6ef5;\n    --spacing: 16px;\n    --radius: 8px;\n}\n\n.button {\n    background: var(--brand);\n    padding: var(--spacing);\n    border-radius: var(--radius);\n}\n```\n\n## Practice\nCreate an animated card component with hover effects and entrance animations.\n',
            "css-final-project": '# Capstone: Landing Page\n\nBuild a complete, responsive landing page from scratch.\n\n## Requirements\n1. Hero section with headline and CTA\n2. Features section (3-4 feature cards)\n3. Testimonials section\n4. Pricing table\n5. Contact form\n6. Responsive navigation\n7. Footer with links\n\n## Design System\n```css\n:root {\n    --primary: #4c6ef5;\n    --text: #212529;\n    --text-secondary: #495057;\n    --bg: #ffffff;\n    --bg-secondary: #f8f9fa;\n    --border: #dee2e6;\n    --radius: 12px;\n    --shadow: 0 4px 24px rgba(0,0,0,0.08);\n}\n```\n\n## Section Skeleton\n```html\n<section class="hero">\n    <div class="container">\n        <h1>Build Something Great</h1>\n        <p>Modern tools for modern teams.</p>\n        <a href="#cta" class="btn">Get Started</a>\n    </div>\n</section>\n```\n\n## Checklist\n- [ ] Mobile-first responsive\n- [ ] Accessible (proper headings, alt text, labels)\n- [ ] Fast loading (optimized images)\n- [ ] Cross-browser compatible\n- [ ] SEO-friendly\n',
        },
    },
}


# Content lookup helper
def _lc(course, module_slug, lesson_slug):
    """Look up lesson content from embedded data."""
    cached = _LC.get(course, {}).get(module_slug, {}).get(lesson_slug)
    if cached and cached != "Content not available.":
        return cached
    # Generate rich default content for lessons without explicit content
    title = lesson_slug.replace("-", " ").replace("_", " ").title()
    mod_title = module_slug.replace("-", " ").replace("_", " ").title()
    return f'''# {title}

Welcome to the **{title}** lesson in the {mod_title} module!

## Overview

This lesson covers essential concepts that will build your programming foundation. Take your time to understand each section thoroughly.

## Key Concepts

- Understanding the core principles
- Writing clean, effective code
- Applying concepts through practice
- Debugging common issues

## Getting Started

```python
# Let's begin exploring!
print("Learning {title}")\n\n# Try experimenting with the concepts below\nname = "Learner"\nprint(f"Welcome, {{name}}! Let's master this topic.")\n```

## Hands-On Practice

1. **Experiment** — Modify the code above and observe results
2. **Apply** — Try using these concepts in new scenarios
3. **Build** — Create something small using what you've learned

## Tips for Success

> 💡 **Pro Tip:** Don't just read — type out every example yourself. Muscle memory is key to programming fluency.

> 🔍 **Debug Mindset:** When something doesn't work, read the error message carefully. It usually tells you exactly what's wrong.

## What's Next?

After mastering this lesson, you'll be ready to tackle more advanced topics. Each lesson builds on the previous ones, so make sure you're comfortable before moving on.

## Quick Reference

```python
# Common patterns you'll use\n# Variables\nx = 10\nname = "value"\n\n# Functions\ndef my_function(param):\n    return param * 2\n\n# Loops\nfor i in range(5):\n    print(i)\n```

Happy coding! 🚀
'''


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as db:
        # Check if seed already ran by looking for the admin user
        result = await db.execute(select(User).where(User.email == "admin@dsir.dev"))
        if result.scalar_one_or_none():
            print("Already seeded. Skipping.")
            return

        print("Seeding DSir database...")

        # ── Users ──
        admin = User(id=uuid4(), email="admin@dsir.dev", username="admin",
            display_name="DSir Admin", password_hash=hash_password("Admin@123!"),
            role="superadmin", email_verified=True, is_active=True)
        db.add(admin)
        db.add(UserStats(user_id=admin.id))

        demo = User(id=uuid4(), email="demo@dsir.dev", username="demo_student",
            display_name="Alex Chen", password_hash=hash_password("Demo@123!"),
            role="student", email_verified=True, is_active=True,
            bio="Aspiring software engineer.")
        db.add(demo)
        db.add(UserStats(user_id=demo.id, total_xp=1250, current_level=5,
            current_streak=7, longest_streak=14, lessons_completed=12, exercises_completed=28))
        await db.flush()

        # ── Categories ──
        cats = {}
        for s, n, d, i in [("programming","Programming Languages","Core programming courses","code"),
            ("web","Web Development","Frontend and backend development","globe"),
            ("data","Data Science & AI","Data science, ML, and AI","brain"),
            ("devops","DevOps & Cloud","Infrastructure and deployment","server")]:
            cats[s] = Category(name=n, slug=s, description=d, icon=i)
            db.add(cats[s])

        # ── Tech Stacks ──
        for s, n, ck in [("python","Python","programming"),("javascript","JavaScript","programming"),
            ("html","HTML","web"),("css","CSS","web"),("react","React","web"),
            ("fastapi","FastAPI","web"),("postgresql","PostgreSQL","data"),
            ("docker","Docker","devops"),("git","Git","devops"),("sql","SQL","data")]:
            db.add(TechnologyStack(name=n, slug=s, category_id=cats[ck].id, is_featured=True))

        # ── Courses ──
        courses = {}

        py_course = Course(id=uuid4(), title="Python Programming: From Zero to Hero",
            slug="python-programming",
            description="Master Python from basics to advanced. Build projects and become job-ready.",
            long_description="Comprehensive Python course: fundamentals, OOP, file handling, projects.",
            learning_objectives=["Write clean Python","Master OOP","Work with files & APIs","Build projects"],
            prerequisites=[], difficulty=DifficultyLevel.BEGINNER,
            estimated_duration_minutes=2400, status=ContentStatus.PUBLISHED,
            skill_tags=["Python","Programming","Backend"], module_count=11, lesson_count=16,
            enrollment_count=15420, rating_average=4.8, rating_count=3240,
            is_featured=True, is_free=True, author_id=admin.id,
            published_at=datetime(2024,1,15,tzinfo=timezone.utc))
        db.add(py_course)
        courses["python"] = py_course

        js_course = Course(id=uuid4(), title="JavaScript: The Complete Guide",
            slug="javascript-complete-guide",
            description="Master JavaScript from fundamentals to async programming. Build interactive web apps.",
            long_description="Complete JS: variables, functions, DOM, async/await, projects.",
            learning_objectives=["JS fundamentals","DOM manipulation","Async programming","Build web apps"],
            prerequisites=[], difficulty=DifficultyLevel.BEGINNER,
            estimated_duration_minutes=1800, status=ContentStatus.PUBLISHED,
            skill_tags=["JavaScript","Web Development","Frontend"], module_count=5, lesson_count=8,
            enrollment_count=12100, rating_average=4.7, rating_count=2890,
            is_featured=True, is_free=True, author_id=admin.id,
            published_at=datetime(2024,2,1,tzinfo=timezone.utc))
        db.add(js_course)
        courses["javascript"] = js_course

        web_course = Course(id=uuid4(), title="HTML & CSS: Build Beautiful Websites",
            slug="html-css-fundamentals",
            description="Build stunning, responsive websites with HTML5 and CSS3.",
            long_description="Master HTML5 semantics, CSS3, Flexbox, Grid, responsive design, animations.",
            learning_objectives=["Semantic HTML5","Modern CSS3","Responsive layouts","Animations"],
            prerequisites=[], difficulty=DifficultyLevel.BEGINNER,
            estimated_duration_minutes=1200, status=ContentStatus.PUBLISHED,
            skill_tags=["HTML","CSS","Web Design"], module_count=4, lesson_count=7,
            enrollment_count=18900, rating_average=4.9, rating_count=4100,
            is_featured=True, is_free=True, author_id=admin.id,
            published_at=datetime(2024,1,10,tzinfo=timezone.utc))
        db.add(web_course)
        courses["htmlcss"] = web_course

        await db.flush()

        # ── Modules & Lessons ──
        structure = {
            "python": [
                ("python-basics","Getting Started with Python","Installation, variables, types, operators, modules, pip",
                 [("hello-world","Your First Python Program","beginner"),
                  ("variables-types","Variables, Data Types & Operators","beginner"),
                  ("modules-pip","Modules, Pip & Understanding Imports","beginner")]),
                ("strings","Strings — The Complete Guide","String indexing, slicing, functions, f-strings, escape sequences",
                 [("strings-intro","Strings — The Complete Guide","beginner")]),
                ("lists-tuples","Lists & Tuples — Data Containers","List indexing, essential methods, tuples, unpacking",
                 [("lists-master","Lists — Your Swiss Army Knife","beginner")]),
                ("dicts-sets","Dictionaries & Sets — Collections","Dict key-value pairs, dict methods, set operations",
                 [("dicts-master","Dictionaries & Sets — Power Data Types","beginner")]),
                ("control-flow","Control Flow — Decisions & Loops","If/elif/else, relational/logical ops, while, for, range",
                 [("conditionals","If/Else — Making Decisions","beginner"),
                  ("loops","Loops — For, While & Beyond","beginner")]),
                ("functions","Functions & Recursion","Function syntax, args & return, default params, recursion",
                 [("functions-master","Functions & Recursion","beginner")]),
                ("file-io","File I/O — Persistent Data","Reading/writing files, with statement, file modes",
                 [("file-handling","File I/O — Reading & Writing Files","intermediate")]),
                ("oop-basics","OOP Fundamentals","Classes, objects, __init__, self, class vs instance, static methods",
                 [("classes-objects","OOP — Classes & Objects","intermediate")]),
                ("oop-advanced","Advanced OOP","Inheritance (single/multiple/multilevel), super(), @property, operator overloading",
                 [("inheritance","Inheritance & Advanced OOP","intermediate")]),
                ("advanced-python","Advanced Python Features","Exception handling, lambda, enumerate, list comprehensions, match case, type hints",
                 [("advanced-features","Advanced Python Features","intermediate")]),
                ("projects","Python Projects","Snake Water Gun game + The Perfect Guess with file I/O",
                 [("snake-water-gun","Project 1: Snake Water Gun Game","intermediate"),
                  ("perfect-guess","Project 2: The Perfect Guess","intermediate")]),
            ],
            "javascript": [
                ("js-basics","JavaScript Fundamentals","Variables, data types, arrays, objects",
                 [("js-intro","JavaScript Fundamentals","beginner"),
                  ("js-arrays-objects","Arrays & Objects","beginner")]),
                ("js-functions","Functions & Scope","Functions, closures, ES6+",
                 [("js-functions-deep","Functions Deep Dive","beginner"),
                  ("js-es6","Modern JavaScript (ES6+)","intermediate")]),
                ("js-dom","DOM & Events","DOM manipulation, events, forms",
                 [("dom-manipulation","DOM Manipulation","beginner"),
                  ("events-forms","Events & Form Handling","beginner")]),
                ("js-async","Asynchronous JavaScript","Promises, async/await, fetch",
                 [("promises-async","Promises & Async/Await","intermediate")]),
                ("js-projects","Projects","Build real applications",
                 [("js-weather-app","Capstone: Weather Dashboard","intermediate")]),
            ],
            "htmlcss": [
                ("html-basics","HTML Fundamentals","Structure, text, links, images, semantic HTML",
                 [("html-intro","Introduction to HTML","beginner"),
                  ("html-semantics","Semantic HTML & Forms","beginner")]),
                ("css-basics","CSS Fundamentals","Selectors, colors, typography, flexbox, grid",
                 [("css-intro","CSS Fundamentals","beginner"),
                  ("css-layout","CSS Layout: Flexbox & Grid","intermediate")]),
                ("responsive-design","Responsive Design","Media queries, fluid layouts, mobile-first",
                 [("responsive-basics","Responsive Design","beginner")]),
                ("css-advanced","Advanced CSS","Animations, transitions, final project",
                 [("animations","CSS Animations & Transitions","intermediate"),
                  ("css-final-project","Capstone: Build a Landing Page","intermediate")]),
            ],
        }

        for course_key, modules_data in structure.items():
            course = courses[course_key]
            tag = course.title.split(":")[0].split()[0]
            for mi, (ms, mt, md, lessons_list) in enumerate(modules_data):
                module = Module(course_id=course.id, title=mt, slug=ms,
                    description=md, display_order=mi+1, lesson_count=len(lessons_list))
                db.add(module)
                await db.flush()

                for li, (ls, lt, ld) in enumerate(lessons_list):
                    # Fetch embedded content
                    content = _lc(course_key, ms, ls)
                    lesson = Lesson(module_id=module.id, title=lt, slug=ls,
                        description=f"Learn {lt.lower()}",
                        content=content, content_markdown=content,
                        learning_objectives=["Understand core concepts","Apply through practice"],
                        difficulty=DifficultyLevel(ld),
                        estimated_duration_minutes=45, display_order=li+1,
                        skill_tags=[tag],
                        status=ContentStatus.PUBLISHED,
                        published_at=datetime.now(timezone.utc))
                    db.add(lesson)
                    await db.flush()

                    ex = Exercise(lesson_id=lesson.id,
                        title=f"Practice: {lt}",
                        description=f"Test your understanding of {lt.lower()}",
                        instructions=f"Complete the challenges",
                        exercise_type=ExerciseType.CODE_COMPLETION,
                        difficulty=ExerciseDifficulty.EASY if ld=="beginner" else ExerciseDifficulty.MEDIUM,
                        starter_code="# Write your solution\n",
                        solution_code="pass\n", test_code="assert True\n",
                        hints=[{"level":1,"content":"Review the lesson material"}],
                        skill_tags=[tag], points=15)
                    db.add(ex)

        # ── Achievements ──
        for name, title, desc, icon, cat, xp in [
            ("python-starter","Python Starter","Complete your first Python lesson","🐍",AchievementCategory.LEARNING,50),
            ("code-warrior","Code Warrior","Complete 10 exercises","⚔️",AchievementCategory.PRACTICE,100),
            ("week-streak","7-Day Streak","Maintain a 7-day learning streak","🔥",AchievementCategory.STREAK,200),
            ("course-complete","Course Graduate","Complete your first course","🎓",AchievementCategory.MILESTONE,500),
            ("perfect-score","Perfect Score","Get 100% on an exercise","⭐",AchievementCategory.PRACTICE,75),
            ("html-master","HTML Hero","Complete all HTML & CSS lessons","🎨",AchievementCategory.LEARNING,300),
            ("js-ninja","JavaScript Ninja","Complete all JavaScript lessons","🥷",AchievementCategory.LEARNING,300),
        ]:
            db.add(Achievement(name=title,description=desc,icon=icon,category=cat,xp_reward=xp,criteria={"type":name}))

        # ── Feature Flags ──
        for name, desc, enabled in [
            ("enable_ai_features","Enable AI features",True),
            ("enable_sandbox","Enable code sandbox",True),
            ("enable_registration","Allow registration",True),
            ("enable_leaderboards","Enable leaderboards",True),
        ]:
            db.add(FeatureFlag(name=name,description=desc,is_enabled=enabled))

        # ── Demo Notifications ──
        for t, title, body in [
            (NotificationType.ACHIEVEMENT,"Achievement Unlocked! 🎉","You earned: Python Starter"),
            (NotificationType.COURSE,"New Course Available","JavaScript: The Complete Guide is live!"),
            (NotificationType.STREAK,"7-Day Streak! 🔥","You've been learning for 7 days straight!"),
        ]:
            db.add(Notification(user_id=demo.id, type=t, title=title, body=body))

        print("✓ DSir database seeded successfully!")
        print("  Admin → admin@dsir.dev / Admin@123!")
        print("  Demo  → demo@dsir.dev  / Demo@123!")
        print(f"  3 courses, {sum(len(md) for md in modules_data)} modules, 26 lessons created")

        await db.commit()


if __name__ == "__main__":
    asyncio.run(seed())
