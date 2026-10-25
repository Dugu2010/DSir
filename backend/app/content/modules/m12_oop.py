"""Module 12 — Object-oriented Python."""

MODULE = {
    "slug": "object-oriented-python",
    "title": "Object-Oriented Python",
    "description": (
        "Model a problem with classes and objects, protect invariants, and "
        "choose inheritance or composition based on the relationship, not habit."
    ),
    "objectives": [
        "Define classes with __init__ and instance methods",
        "Explain self, attributes, and encapsulation",
        "Use inheritance for genuine is-a relationships",
        "Prefer composition for assembling behaviour",
        "Use dataclasses for simple data containers",
    ],
    "estimated_duration_minutes": 115,
    "lessons": [
        {
            "slug": "classes-objects-encapsulation",
            "title": "Classes, Objects, and Encapsulation",
            "description": (
                "Turn related data and behaviour into a coherent object, with "
                "validation that protects its invariants."
            ),
            "difficulty": "intermediate",
            "minutes": 50,
            "tags": ["python", "oop", "classes", "encapsulation"],
            "objectives": [
                "Create a class with an initialiser and methods",
                "Explain what self refers to",
                "Validate attributes so objects cannot enter invalid states",
            ],
            "resources": [
                {
                    "title": "Python Tutorial — Classes",
                    "url": "https://docs.python.org/3/tutorial/classes.html",
                    "resource_type": "reference",
                },
                {
                    "title": "dataclasses documentation",
                    "url": "https://docs.python.org/3/library/dataclasses.html",
                    "resource_type": "reference",
                },
            ],
            "content": r'''# Classes, Objects, and Encapsulation

## A class is a blueprint; an object is an instance

```python
class BankAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("deposit must be positive")
        self.balance += amount

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("withdrawal must be positive")
        if amount > self.balance:
            raise ValueError("insufficient funds")
        self.balance -= amount


account = BankAccount("Ada", 100)
account.deposit(50)
account.withdraw(30)
print(account.balance)  # 120
```

`self` is the instance the method was called on. `account.deposit(50)` is effectively `BankAccount.deposit(account, 50)`.

## Why use a class here?

The account's balance and the rules that protect it belong together. A dictionary plus loose functions would allow this:

```python
account = {"balance": 100}
account["balance"] = -9999   # nothing stops it
```

A class cannot make Python enforce privacy, but it gives you a single place to validate changes. That is encapsulation in practice: keep state and the rules for changing it together.

## Convention, not secrecy

```python
self.balance          # public
self._balance         # internal by convention
self.__balance        # name-mangled; not a security boundary
```

Use one underscore for “this is internal.” Do not call it security. Python is an open language; the contract is social and documented.

## Magic methods

```python
class Money:
    def __init__(self, cents):
        self.cents = cents

    def __repr__(self):
        return f"Money({self.cents})"

    def __eq__(self, other):
        return isinstance(other, Money) and self.cents == other.cents

    def __add__(self, other):
        return Money(self.cents + other.cents)
```

`__repr__` helps debugging. `__eq__` defines value equality. `__add__` lets instances support `+`. Add these when they make the object behave naturally, not to show off.

## Dataclasses

For a simple data container, a dataclass removes boilerplate:

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float


point = Point(2, 3)
print(point)
```

You still get normal classes and methods when behaviour grows.

## Common mistakes

- Forgetting `self` in method definitions or calls.
- Using a mutable class attribute as if it were per-instance state.
- Creating god objects that know everything.
- Using inheritance before checking whether composition is simpler.
- Exposing attributes that can be changed into invalid states.

## Guided practice

Predict:

```python
p = Point(1, 2)
q = Point(1, 2)
print(p == q)
```

With a plain class and no `__eq__`, this is `False` because identity is compared. With a dataclass, it is `True` because equality is generated.

## Independent practice

Create `Temperature` with a Celsius value, validation preventing below absolute zero, and methods `to_fahrenheit()` and a useful `__repr__`.

## Summary

Classes bundle state and behaviour. `self` connects methods to instances. Validation protects invariants. Use dataclasses for plain records and add behaviour only when it belongs to the object.

## Further reading

- [Python Tutorial — Classes](https://docs.python.org/3/tutorial/classes.html)
- [dataclasses](https://docs.python.org/3/library/dataclasses.html)
''',
            "exercises": [
                {
                    "title": "Build a validated bank account",
                    "description": "Protect object state with clear rules.",
                    "instructions": (
                        "Complete BankAccount with deposit and withdraw. Reject "
                        "non-positive amounts and overdrafts with ValueError. "
                        "Expose a balance attribute starting at 0."
                    ),
                    "type": "code_completion",
                    "difficulty": "medium",
                    "starter": 'class BankAccount:\n    def __init__(self):\n        self.balance = 0\n\n    def deposit(self, amount):\n        pass\n\n    def withdraw(self, amount):\n        pass\n',
                    "solution": 'class BankAccount:\n    def __init__(self):\n        self.balance = 0\n\n    def deposit(self, amount):\n        if amount <= 0:\n            raise ValueError("deposit must be positive")\n        self.balance += amount\n\n    def withdraw(self, amount):\n        if amount <= 0:\n            raise ValueError("withdrawal must be positive")\n        if amount > self.balance:\n            raise ValueError("insufficient funds")\n        self.balance -= amount\n',
                    "tests": 'account = BankAccount()\naccount.deposit(100)\naccount.withdraw(30)\nassert account.balance == 70\ntry:\n    account.withdraw(1000)\n    raise AssertionError("expected ValueError")\nexcept ValueError:\n    pass\ntry:\n    account.deposit(0)\n    raise AssertionError("expected ValueError")\nexcept ValueError:\n    pass\n',
                    "hints": [
                        "Check amount <= 0 first.",
                        "Check the balance before subtracting.",
                    ],
                    "points": 15,
                    "minutes": 15,
                    "tags": ["python", "oop", "validation"],
                },
            ],
            "quiz": None,
        },
        {
            "slug": "inheritance-composition-dataclasses",
            "title": "Inheritance, Composition, and Dataclasses",
            "description": (
                "Use inheritance for true is-a relationships, composition for "
                "has-a relationships, and dataclasses for boring data."
            ),
            "difficulty": "intermediate",
            "minutes": 45,
            "tags": ["python", "oop", "inheritance", "composition", "dataclasses"],
            "objectives": [
                "Override a method safely with super()",
                "Identify when composition is the better design",
                "Use dataclasses for value objects",
            ],
            "resources": [
                {
                    "title": "Python Tutorial — Inheritance",
                    "url": "https://docs.python.org/3/tutorial/classes.html#inheritance",
                    "resource_type": "reference",
                },
                {
                    "title": "dataclasses",
                    "url": "https://docs.python.org/3/library/dataclasses.html",
                    "resource_type": "reference",
                },
            ],
            "content": r'''# Inheritance, Composition, and Dataclasses

## Inheritance models is-a

```python
class Shape:
    def area(self):
        raise NotImplementedError

    def describe(self):
        return f"{type(self).__name__} with area {self.area():.2f}"


class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height


class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return 3.14159 * self.radius ** 2
```

A rectangle **is a** shape. That relationship justifies inheritance. `describe()` can be written once in the base class and still call the subclass's `area()` — polymorphism.

## super() extends behaviour

```python
class SavingsAccount(BankAccount):
    def __init__(self, owner, balance=0, rate=0.02):
        super().__init__(owner, balance)
        self.rate = rate

    def add_interest(self):
        self.deposit(self.balance * self.rate)
```

`super()` runs the parent initialiser so you do not duplicate its logic.

## Composition models has-a

```python
class Logger:
    def log(self, message):
        print(f"[LOG] {message}")


class OrderService:
    def __init__(self, logger):
        self.logger = logger

    def place(self, order_id):
        self.logger.log(f"order {order_id} placed")
```

An order service **has a** logger. It is not a kind of logger. Composition keeps coupling flexible and makes testing easy: pass a fake logger.

Prefer composition when unsure. Inheritance creates tight coupling and fragile hierarchies; use it when the subtype genuinely substitutes for the parent.

## Abstract base classes

```python
from abc import ABC, abstractmethod


class PaymentMethod(ABC):
    @abstractmethod
    def charge(self, amount):
        ...


class CardPayment(PaymentMethod):
    def charge(self, amount):
        print(f"charged {amount} to card")
```

Instantiating `PaymentMethod` directly fails, which makes the contract explicit.

## Dataclasses

```python
from dataclasses import dataclass, field


@dataclass
class Order:
    customer: str
    items: list[str] = field(default_factory=list)

    @property
    def item_count(self):
        return len(self.items)
```

Use `field(default_factory=list)` instead of `items: list[str] = []`. The latter shares one list across instances, the same mutable-default trap from functions.

## Common mistakes

- Inheriting because it saves typing, not because the relationship holds.
- Forgetting `super().__init__` and missing parent state.
- Deep hierarchies with five levels of overrides.
- Using mutable defaults in dataclasses.
- Assuming `__eq__` works by value without defining it (plain classes compare identity).

## Guided practice

Design a `Notification` base class with `send()`. Create `EmailNotification` and `SMSNotification`. Then explain why an `Order` containing a notifier is composition, while `EmailNotification` inheriting `Notification` is inheritance.

## Independent practice

Refactor a `Report` class that both formats text and emails it into two classes: a formatter and a mailer. Compose them in a `ReportService`.

## Summary

Inheritance expresses is-a and enables polymorphism. Composition expresses has-a and usually ages better. Dataclasses remove boilerplate for records. Protect invariants and keep hierarchies shallow.

## Further reading

- [Inheritance](https://docs.python.org/3/tutorial/classes.html#inheritance)
- [abc — Abstract Base Classes](https://docs.python.org/3/library/abc.html)
- [dataclasses](https://docs.python.org/3/library/dataclasses.html)
''',
            "exercises": [
                {
                    "title": "Shape area polymorphism",
                    "description": "Implement subclasses that satisfy a shared contract.",
                    "instructions": (
                        "Complete Rectangle and Circle so their area() methods work. "
                        "Use 3.14159 for pi. Each constructor stores its dimensions."
                    ),
                    "type": "code_completion",
                    "difficulty": "medium",
                    "starter": 'class Shape:\n    def area(self):\n        raise NotImplementedError\n\n\nclass Rectangle(Shape):\n    def __init__(self, width, height):\n        pass\n\n    def area(self):\n        pass\n\n\nclass Circle(Shape):\n    def __init__(self, radius):\n        pass\n\n    def area(self):\n        pass\n',
                    "solution": 'class Shape:\n    def area(self):\n        raise NotImplementedError\n\n\nclass Rectangle(Shape):\n    def __init__(self, width, height):\n        self.width = width\n        self.height = height\n\n    def area(self):\n        return self.width * self.height\n\n\nclass Circle(Shape):\n    def __init__(self, radius):\n        self.radius = radius\n\n    def area(self):\n        return 3.14159 * self.radius ** 2\n',
                    "tests": 'assert Rectangle(3, 4).area() == 12\nassert round(Circle(1).area(), 5) == 3.14159\nassert round(Circle(2).area(), 4) == 12.5664\n',
                    "hints": [
                        "Store constructor arguments on self.",
                        "Circle area is pi times radius squared.",
                    ],
                    "points": 15,
                    "minutes": 14,
                    "tags": ["python", "oop", "inheritance"],
                },
            ],
            "quiz": None,
        },
    ],
    "quiz": {
        "title": "Module 12 Assessment — OOP",
        "description": "Check object state, inheritance, and composition decisions.",
        "passing_score": 70,
        "questions": [
            {
                "content": "What does `self` refer to inside an instance method?",
                "options": [
                    ("The object the method was called on", True),
                    ("The class definition", False),
                    ("The parent module", False),
                    ("A global variable", False),
                ],
                "explanation": "Python passes the instance as the first argument automatically.",
            },
            {
                "content": "Which relationship best justifies inheritance?",
                "options": [
                    ("A savings account is a bank account", True),
                    ("An order has a logger", False),
                    ("A report uses a formatter", False),
                    ("A service has a database connection", False),
                ],
                "explanation": "Inheritance should model an is-a relationship.",
            },
            {
                "content": "Why use `field(default_factory=list)` in a dataclass?",
                "options": [
                    ("Each instance gets its own list", True),
                    ("It makes the list immutable", False),
                    ("It sorts the list", False),
                    ("It is required for all fields", False),
                ],
                "explanation": "A mutable default would be shared between instances.",
            },
            {
                "content": "What does an abstract method do?",
                "options": [
                    ("Declares a method subclasses must implement", True),
                    ("Runs before __init__", False),
                    ("Makes a class final", False),
                    ("Caches the result", False),
                ],
                "explanation": "Abstract base classes make the required interface explicit.",
            },
        ],
    },
    "projects": [],
}
