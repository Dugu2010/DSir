import asyncio
import base64
import logging
import uuid
from typing import Any

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import AsyncSessionLocal
from src.models.assessment import Project
from src.models.content import Concept, Course, Lesson, Roadmap, RoadmapCourse


def _to_b64(text: str) -> str:
    return base64.b64encode(text.encode("utf-8")).decode("ascii")


def _course_thumbnail(title: str) -> str:
    """Return a deterministic SVG gradient banner for a course.

    Using inline SVG avoids broken external image links and keeps the app
    looking premium without relying on third-party image hosts.
    """
    # Generate a stable hue from the course title
    hue = sum(ord(c) for c in title) % 360
    hue2 = (hue + 40) % 360
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 450">
  <defs>
    <linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="hsl({hue}, 80%, 55%)" />
      <stop offset="100%" stop-color="hsl({hue2}, 80%, 45%)" />
    </linearGradient>
  </defs>
  <rect width="800" height="450" fill="url(#g)" />
  <circle cx="700" cy="80" r="120" fill="rgba(255,255,255,0.12)" />
  <circle cx="100" cy="350" r="150" fill="rgba(255,255,255,0.08)" />
  <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle"
        fill="white" font-family="system-ui, -apple-system, sans-serif" font-size="48" font-weight="700">
    {title}
  </text>
</svg>"""
    return f"data:image/svg+xml;base64,{_to_b64(svg)}"


_CODE_EXAMPLES: dict[str, list[tuple[str, str]]] = {
    "python": [
        ("python", "# Variables and data types\nname = 'Alice'\nage = 30\nprint(f'{name} is {age}')"),
        ("python", "# Conditional logic\nscore = 85\nif score >= 80:\n    print('Great job!')"),
        ("python", "# Function definition\ndef greet(name):\n    return f'Hello, {name}'\nprint(greet('DSir'))"),
        ("python", "# List comprehension\nsquares = [x**2 for x in range(10)]\nprint(squares)"),
        ("python", "# Dictionary usage\nuser = {'name': 'Alice', 'role': 'admin'}\nprint(user.get('role'))"),
        ("python", "# File I/O with context manager\nwith open('data.txt', 'w') as f:\n    f.write('Hello, file!')"),
        ("python", "# JSON serialization\nimport json\ndata = {'users': []}\nwith open('data.json', 'w') as f:\n    json.dump(data, f, indent=2)"),
        ("python", "# Error handling\ntry:\n    value = int(input('Number: '))\nexcept ValueError:\n    print('Invalid input')"),
        ("python", "# Decorator\nimport functools\n\ndef timer(func):\n    @functools.wraps(func)\n    def wrapper(*args, **kwargs):\n        import time\n        start = time.time()\n        result = func(*args, **kwargs)\n        print(f'Took {time.time() - start:.2f}s')\n        return result\n    return wrapper"),
        ("python", "# Asyncio coroutine\nimport asyncio\n\nasync def main():\n    await asyncio.sleep(1)\n    print('done')\n\nasyncio.run(main())"),
        ("python", "# Generator\ndef fibonacci(n):\n    a, b = 0, 1\n    for _ in range(n):\n        yield a\n        a, b = b, a + b\n\nprint(list(fibonacci(10)))"),
        ("python", "# Class definition\nclass User:\n    def __init__(self, name):\n        self.name = name\n\n    def greet(self):\n        return f'Hello, {self.name}'\n\nprint(User('DSir').greet())"),
    ],
    "html": [
        ("html", "<h1>Hello World</h1>\n<p>Welcome to DSir.</p>"),
        ("css", "body {\n  background: #f8fafc;\n  color: #0f172a;\n}"),
        ("html", "<button class='btn'>Click me</button>"),
        ("css", ".btn {\n  padding: 0.5rem 1rem;\n  border-radius: 0.375rem;\n}"),
        ("html", "<form>\n  <label for='email'>Email</label>\n  <input id='email' type='email' required>\n</form>"),
        ("css", ".grid {\n  display: grid;\n  grid-template-columns: repeat(3, 1fr);\n  gap: 1rem;\n}"),
        ("html", "<picture>\n  <source srcset='large.jpg' media='(min-width: 800px)'>\n  <img src='small.jpg' alt='Responsive'>\n</picture>"),
        ("css", "@media (min-width: 768px) {\n  .container { display: flex; }\n}"),
        ("html", "<link rel='preload' href='hero.css' as='style'>"),
        ("css", ":root {\n  --primary: #6366f1;\n}\nbutton { background: var(--primary); }"),
        ("html", "<div role='dialog' aria-modal='true' aria-labelledby='title'>...</div>"),
        ("css", "@container (min-width: 400px) {\n  .card { display: flex; }\n}"),
    ],
    "css": [
        ("css", "body {\n  background: #f8fafc;\n  color: #0f172a;\n}"),
        ("css", ".btn {\n  padding: 0.5rem 1rem;\n  border-radius: 0.375rem;\n}"),
        ("css", ".grid {\n  display: grid;\n  grid-template-columns: repeat(3, 1fr);\n  gap: 1rem;\n}"),
        ("css", "@media (min-width: 768px) {\n  .container { display: flex; }\n}"),
        ("css", ":root {\n  --primary: #6366f1;\n}\nbutton { background: var(--primary); }"),
        ("css", "@container (min-width: 400px) {\n  .card { display: flex; }\n}"),
        ("css", "@keyframes fadeIn {\n  from { opacity: 0; }\n  to { opacity: 1; }\n}"),
        ("css", "@keyframes slideUp {\n  from { transform: translateY(20px); opacity: 0; }\n  to { transform: translateY(0); opacity: 1; }\n}"),
        ("html", "<div role='dialog' aria-modal='true' aria-labelledby='title'>...</div>"),
        ("css", ":root {\n  --primary: #6366f1;\n  --text: #0f172a;\n  --bg: #f8fafc;\n}"),
        ("css", ".card:hover {\n  transform: translateY(-4px);\n  box-shadow: 0 12px 24px rgba(0,0,0,0.1);\n}"),
        ("css", "@media (prefers-color-scheme: dark) {\n  body { background: #0f172a; color: #f8fafc; }\n}"),
    ],
    "javascript": [
        ("javascript", "const greeting = 'Hello DSir';\nconsole.log(greeting);"),
        ("javascript", "const nums = [1, 2, 3];\nconst doubled = nums.map(n => n * 2);"),
        ("javascript", "async function fetchData() {\n  const res = await fetch('/api/data');\n  return res.json();\n}"),
        ("javascript", "document.querySelector('#btn').addEventListener('click', () => {\n  console.log('clicked');\n});"),
        ("javascript", "const doubled = nums.map(n => n * 2);"),
        ("javascript", "const { name, age } = user;"),
        ("javascript", "fetch('/api').then(r => r.json()).then(console.log);"),
        ("javascript", "import { helper } from './helper.js';"),
        ("javascript", "const debounce = (fn, delay) => {\n  let id;\n  return (...args) => {\n    clearTimeout(id);\n    id = setTimeout(() => fn(...args), delay);\n  };\n};"),
        ("javascript", "class EventEmitter {\n  constructor() { this.listeners = {}; }\n  on(event, cb) {\n    (this.listeners[event] ||= []).push(cb);\n  }\n  emit(event, data) {\n    (this.listeners[event] || []).forEach(cb => cb(data));\n  }\n}"),
        ("javascript", "const event = new CustomEvent('lesson:complete', { detail: { id: 1 } });\ndocument.dispatchEvent(event);"),
        ("javascript", "const memoize = (fn) => {\n  const cache = {};\n  return (arg) => cache[arg] ?? (cache[arg] = fn(arg));\n};"),
    ],
    "typescript": [
        ("typescript", "type User = {\n  id: string;\n  email: string;\n};\nconst u: User = { id: '1', email: 'a@b.com' };"),
        ("typescript", "function add(a: number, b: number): number {\n  return a + b;\n}"),
        ("typescript", "interface Course {\n  title: string;\n  duration: number;\n}"),
    ],
    "react": [
        ("tsx", "function Welcome({ name }: { name: string }) {\n  return <h1>Hello, {name}</h1>;\n}"),
        ("tsx", "const [count, setCount] = useState(0);"),
        ("tsx", "useEffect(() => {\n  console.log('mounted');\n}, []);"),
    ],
    "nextjs": [
        ("tsx", "export default function Page() {\n  return <h1>My Page</h1>;\n}"),
        ("tsx", "export async function generateStaticParams() {\n  return [{ id: '1' }];\n}"),
        ("typescript", "export const revalidate = 60;"),
    ],
    "fastapi": [
        ("python", "from fastapi import FastAPI\napp = FastAPI()\n\n@app.get('/')\ndef read_root():\n    return {'ok': True}"),
        ("python", "from pydantic import BaseModel\nclass Item(BaseModel):\n    name: str\n    price: float"),
        ("python", "@app.get('/items/{item_id}')\ndef read_item(item_id: int):\n    return {'item_id': item_id}"),
    ],
    "sql": [
        ("sql", "SELECT id, title FROM courses WHERE is_published = true;"),
        ("sql", "SELECT c.title, COUNT(l.id) FROM courses c\nJOIN lessons l ON l.course_id = c.id\nGROUP BY c.title;"),
        ("sql", "INSERT INTO users (email) VALUES ('alice@example.com');"),
    ],
    "postgresql": [
        ("sql", "CREATE TABLE users (\n  id UUID PRIMARY KEY,\n  email TEXT NOT NULL\n);"),
        ("sql", "CREATE INDEX idx_users_email ON users(email);"),
        ("sql", "SELECT * FROM users WHERE email ILIKE '%@example.com';"),
    ],
    "docker": [
        ("dockerfile", "FROM python:3.11-slim\nWORKDIR /app\nCOPY . .\nCMD ['python', 'app.py']"),
        ("bash", "docker build -t dsir-api .\ndocker run -p 8000:8000 dsir-api"),
        ("yaml", "version: '3.9'\nservices:\n  app:\n    image: dsir-api"),
    ],
    "linux": [
        ("bash", "ls -la /var/log\ncd /home/user"),
        ("bash", "chmod +x script.sh\n./script.sh"),
        ("bash", "sudo systemctl restart nginx"),
    ],
    "ai": [
        ("python", "from openai import OpenAI\nclient = OpenAI()\nresponse = client.chat.completions.create(\n    model='gpt-4o',\n    messages=[{'role': 'user', 'content': 'Hello'}]\n)"),
        ("python", "# Prompt template\nprompt = f'Answer as an expert: {question}'"),
        ("python", "# RAG retrieval\nchunks = vector_store.similarity_search(query, k=5)"),
    ],
    "ml": [
        ("python", "from sklearn.linear_model import LinearRegression\nmodel = LinearRegression()\nmodel.fit(X, y)"),
        ("python", "from sklearn.model_selection import train_test_split\nX_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)"),
        ("python", "import pandas as pd\ndf = pd.read_csv('data.csv')\nprint(df.head())"),
    ],
    "git": [
        ("bash", "git init\ngit add .\ngit commit -m 'initial commit'"),
        ("bash", "git checkout -b feature/new-ui\ngit push -u origin feature/new-ui"),
        ("bash", "git pull origin main --rebase"),
    ],
}


def _course_modules(language: str) -> list[str]:
    return ["Beginner Foundations", "Intermediate Concepts", "Advanced Mastery", "Real-World Projects"]


_COURSE_DEFINITIONS: list[dict[str, Any]] = [
    # Core languages — one course each, with beginner → advanced modules
    {
        "slug": "python",
        "title": "Python",
        "description": "A complete path from Python basics to advanced topics like decorators, concurrency, and production-ready patterns.",
        "category": "Backend",
        "programming_language": "Python",
        "technology": "Python",
        "difficulty": "beginner",
        "skills": [
            "Variables & Types",
            "Control Flow",
            "Functions & Modules",
            "OOP",
            "File I/O",
            "Asyncio",
            "Decorators",
            "Production Patterns",
        ],
        "modules": _course_modules("python"),
    },
    {
        "slug": "javascript",
        "title": "JavaScript",
        "description": "Master JavaScript from the fundamentals through closures, async programming, and advanced design patterns.",
        "category": "Frontend",
        "programming_language": "JavaScript",
        "technology": "JavaScript",
        "difficulty": "beginner",
        "skills": [
            "Variables & Types",
            "DOM & Events",
            "Async/Await",
            "Closures",
            "ES6+",
            "Design Patterns",
            "Testing",
            "Performance",
        ],
        "modules": _course_modules("javascript"),
    },
    {
        "slug": "html",
        "title": "HTML",
        "description": "Build semantic, accessible, and performant web pages with HTML from the ground up.",
        "category": "Frontend",
        "programming_language": "HTML/CSS",
        "technology": "HTML",
        "difficulty": "beginner",
        "skills": [
            "Semantic Markup",
            "Forms & Validation",
            "Accessibility",
            "Multimedia",
            "SEO",
            "Templates",
            "Custom Elements",
            "Email HTML",
        ],
        "modules": _course_modules("html"),
    },
    {
        "slug": "css",
        "title": "CSS",
        "description": "Style the web with confidence: selectors, layouts, responsive design, animations, and modern architecture.",
        "category": "Frontend",
        "programming_language": "HTML/CSS",
        "technology": "CSS",
        "difficulty": "beginner",
        "skills": [
            "Selectors & Box Model",
            "Flexbox & Grid",
            "Responsive Design",
            "Custom Properties",
            "Animations",
            "Container Queries",
            "Architecture",
            "Sass",
        ],
        "modules": _course_modules("css"),
    },
    # Secondary topics — each is a single focused course
    {
        "slug": "git-and-github",
        "title": "Git & GitHub",
        "description": "Learn version control with Git and collaborate effectively using GitHub.",
        "category": "DevOps",
        "programming_language": "Git",
        "technology": "Git",
        "difficulty": "beginner",
        "skills": ["Git", "GitHub", "Branching", "Merging", "Pull Requests"],
        "modules": ["Version Control Basics", "Branching & Merging", "Collaboration", "Advanced Git"],
    },
    {
        "slug": "typescript-essentials",
        "title": "TypeScript Essentials",
        "description": "Add static typing to your JavaScript projects with TypeScript.",
        "category": "Frontend",
        "programming_language": "TypeScript",
        "technology": "TypeScript",
        "difficulty": "intermediate",
        "skills": ["TypeScript", "Types", "Interfaces", "Generics", "TS Config"],
        "modules": ["Types & Interfaces", "Functions & Objects", "Generics", "Advanced Types"],
    },
    {
        "slug": "react-fundamentals",
        "title": "React Fundamentals",
        "description": "Build interactive UIs with React hooks, components, and modern patterns.",
        "category": "Frontend",
        "programming_language": "JavaScript",
        "technology": "React",
        "difficulty": "intermediate",
        "skills": ["React", "Hooks", "Components", "State", "Effects"],
        "modules": ["Components & JSX", "State & Events", "Hooks", "Patterns"],
    },
    {
        "slug": "nextjs-mastery",
        "title": "Next.js Mastery",
        "description": "Create production-grade full-stack apps with Next.js App Router.",
        "category": "Full Stack",
        "programming_language": "TypeScript",
        "technology": "Next.js",
        "difficulty": "intermediate",
        "skills": ["Next.js", "App Router", "SSR", "API Routes", "Deployment"],
        "modules": ["App Router", "Routing & Layouts", "Data Fetching", "Deployment"],
    },
    {
        "slug": "fastapi-mastery",
        "title": "FastAPI Mastery",
        "description": "Build high-performance Python APIs with FastAPI, Pydantic, and SQLAlchemy.",
        "category": "Backend",
        "programming_language": "Python",
        "technology": "FastAPI",
        "difficulty": "intermediate",
        "skills": ["FastAPI", "Pydantic", "SQLAlchemy", "Dependency Injection", "Async"],
        "modules": ["Routing & Schemas", "Databases", "Authentication", "Testing & Deployment"],
    },
    {
        "slug": "sql-fundamentals",
        "title": "SQL Fundamentals",
        "description": "Write powerful queries and design relational databases with SQL.",
        "category": "Backend",
        "programming_language": "SQL",
        "technology": "SQL",
        "difficulty": "beginner",
        "skills": ["SQL", "Queries", "Joins", "Aggregations", "Indexes"],
        "modules": ["SELECT & Filtering", "Joins", "Aggregations", "Indexes & Optimization"],
    },
    {
        "slug": "postgresql-mastery",
        "title": "PostgreSQL Mastery",
        "description": "Master PostgreSQL: advanced queries, indexing, full-text search, and JSONB.",
        "category": "Backend",
        "programming_language": "SQL",
        "technology": "PostgreSQL",
        "difficulty": "advanced",
        "skills": ["PostgreSQL", "JSONB", "Indexes", "Full-Text Search", "Window Functions"],
        "modules": ["Advanced Queries", "Indexing", "JSONB", "Extensions"],
    },
    {
        "slug": "docker-essentials",
        "title": "Docker Essentials",
        "description": "Containerize applications and orchestrate services with Docker.",
        "category": "DevOps",
        "programming_language": "Docker",
        "technology": "Docker",
        "difficulty": "intermediate",
        "skills": ["Docker", "Containers", "Images", "Docker Compose", "Networking"],
        "modules": ["Containers & Images", "Dockerfiles", "Docker Compose", "Networking"],
    },
    {
        "slug": "linux-fundamentals",
        "title": "Linux Fundamentals",
        "description": "Navigate the command line and manage Linux servers with confidence.",
        "category": "DevOps",
        "programming_language": "Linux",
        "technology": "Linux",
        "difficulty": "beginner",
        "skills": ["Linux", "CLI", "Permissions", "Processes", "Shell Scripting"],
        "modules": ["Command Line Basics", "File System", "Users & Permissions", "Shell Scripting"],
    },
    {
        "slug": "ai-engineering",
        "title": "AI Engineering",
        "description": "Build production AI applications with LLMs, embeddings, and agents.",
        "category": "AI",
        "programming_language": "Python",
        "technology": "AI",
        "difficulty": "advanced",
        "skills": ["LLMs", "Prompt Engineering", "RAG", "Embeddings", "Agents"],
        "modules": ["LLM Basics", "Prompt Engineering", "RAG", "Agents & Tools"],
    },
    {
        "slug": "machine-learning-fundamentals",
        "title": "Machine Learning Fundamentals",
        "description": "Understand the foundations of machine learning and train models with Python.",
        "category": "AI",
        "programming_language": "Python",
        "technology": "Machine Learning",
        "difficulty": "intermediate",
        "skills": ["ML", "Scikit-Learn", "Pandas", "Regression", "Classification"],
        "modules": ["ML Workflow", "Regression", "Classification", "Model Evaluation"],
    },
]

_PROJECT_DEFINITIONS: list[dict[str, Any]] = [
    {
        "slug": "python-cli-quiz",
        "course_slug": "python",
        "title": "Python CLI Quiz Game",
        "description": "Build a command-line quiz game with multiple categories, scoring, and a leaderboard.",
        "requirements": {
            "objectives": [
                "Read quiz questions from a JSON file",
                "Track the player's score across multiple rounds",
                "Store high scores in a local file",
                "Provide a clean command-line interface",
            ],
            "must_have": ["JSON data loading", "Score tracking", "Persistent leaderboard"],
            "nice_to_have": ["Difficulty levels", "Timed rounds", "Colorful output"],
        },
        "starter_files": {
            "main.py": "import json\nimport random\n\ndef load_questions():\n    with open('questions.json') as f:\n        return json.load(f)['questions']\n\ndef run_quiz():\n    questions = load_questions()\n    random.shuffle(questions)\n    score = 0\n    for q in questions[:5]:\n        print(q['question'])\n        for i, opt in enumerate(q['options']):\n            print(f\"{i + 1}. {opt}\")\n        answer = input('Your answer: ')\n        if answer.strip().lower() == q['answer'].lower():\n            score += 1\n    print(f\"You scored {score}/5\")\n\nif __name__ == '__main__':\n    run_quiz()\n",
            "questions.json": '{"questions": [{"question": "What is the output of print(2 + 3 * 4)?", "options": ["20", "14", "11", "24"], "answer": "14"}]}',
        },
    },
    {
        "slug": "python-csv-analyzer",
        "course_slug": "python",
        "title": "CSV Data Analyzer",
        "description": "Write a script that reads a CSV file, calculates statistics, and prints a summary report.",
        "requirements": {
            "objectives": [
                "Parse CSV files with the csv module",
                "Compute basic statistics (min, max, average)",
                "Handle missing or invalid data gracefully",
                "Output a formatted report",
            ],
            "must_have": ["CSV parsing", "Error handling", "Formatted output"],
            "nice_to_have": ["Charts", "Filtering", "Export to JSON"],
        },
        "starter_files": {
            "main.py": "import csv\nfrom collections import defaultdict\n\ndef analyze_csv(filename):\n    scores = []\n    with open(filename, newline='') as f:\n        reader = csv.DictReader(f)\n        for row in reader:\n            scores.append(int(row['score']))\n    return {\n        'count': len(scores),\n        'average': sum(scores) / len(scores),\n        'max': max(scores),\n        'min': min(scores),\n    }\n\nif __name__ == '__main__':\n    stats = analyze_csv('data.csv')\n    for key, value in stats.items():\n        print(f\"{key}: {value}\")\n",
            "data.csv": "name,score\nAlice,85\nBob,92\nCharlie,78\nDiana,95\n",
        },
    },
    {
        "slug": "html-css-landing-page",
        "course_slug": "css",
        "title": "Responsive Landing Page",
        "description": "Build a responsive landing page for a fictional product using semantic HTML and CSS.",
        "requirements": {
            "objectives": [
                "Use semantic HTML tags",
                "Implement a mobile-first responsive layout",
                "Add a contact form with validation",
                "Use CSS custom properties for theming",
            ],
            "must_have": ["Semantic HTML", "Responsive layout", "Styled form"],
            "nice_to_have": ["Animations", "Dark mode", "Accessibility improvements"],
        },
        "starter_files": {
            "index.html": "<!DOCTYPE html>\n<html lang=\\\"en\\\">\n<head>\n  <meta charset=\\\"UTF-8\">\n  <meta name=\\\"viewport\\\" content=\\\"width=device-width, initial-scale=1.0\">\n  <title>DSir Product</title>\n  <link rel=\\\"stylesheet\\\" href=\\\"styles.css\">\n</head>\n<body>\n  <header>\n    <h1>DSir Product</h1>\n    <p>The best way to learn programming.</p>\n  </header>\n  <main>\n    <section>\n      <h2>Features</h2>\n      <ul>\n        <li>Interactive lessons</li>\n        <li>AI mentor</li>\n      </ul>\n    </section>\n    <section>\n      <h2>Contact</h2>\n      <form>\n        <label for=\\\"email\\\">Email:</label>\n        <input type=\\\"email\\\" id=\\\"email\\\" required>\n        <button type=\\\"submit\\\">Join</button>\n      </form>\n    </section>\n  </main>\n</body>\n</html>\n",
            "styles.css": ":root {\n  --primary: #6366f1;\n  --text: #0f172a;\n  --bg: #f8fafc;\n}\n\n* {\n  box-sizing: border-box;\n  margin: 0;\n  padding: 0;\n}\n\nbody {\n  font-family: system-ui, -apple-system, sans-serif;\n  background: var(--bg);\n  color: var(--text);\n  line-height: 1.6;\n}\n\nheader {\n  text-align: center;\n  padding: 4rem 1rem;\n  background: var(--primary);\n  color: white;\n}\n\nmain {\n  max-width: 800px;\n  margin: 0 auto;\n  padding: 2rem 1rem;\n}\n\nsection {\n  margin-bottom: 2rem;\n}\n\nform {\n  display: flex;\n  flex-direction: column;\n  gap: 0.5rem;\n  max-width: 400px;\n}\n\nbutton {\n  padding: 0.5rem 1rem;\n  background: var(--primary);\n  color: white;\n  border: none;\n  border-radius: 0.375rem;\n  cursor: pointer;\n}\n",
        },
    },
    {
        "slug": "js-todo-app",
        "course_slug": "javascript",
        "title": "To-Do List App",
        "description": "Build an interactive to-do list with add, complete, and delete functionality.",
        "requirements": {
            "objectives": [
                "Add new tasks",
                "Mark tasks as complete",
                "Delete tasks",
                "Persist tasks in localStorage",
            ],
            "must_have": ["CRUD operations", "DOM updates", "localStorage"],
            "nice_to_have": ["Filters", "Animations", "Drag and drop"],
        },
        "starter_files": {
            "index.html": "<!DOCTYPE html>\n<html lang=\\\"en\\\">\n<head>\n  <meta charset=\\\"UTF-8\">\n  <meta name=\\\"viewport\\\" content=\\\"width=device-width, initial-scale=1.0\">\n  <title>DSir To-Do</title>\n  <link rel=\\\"stylesheet\\\" href=\\\"styles.css\">\n</head>\n<body>\n  <div class=\\\"app\\\">\n    <h1>To-Do List</h1>\n    <form id=\\\"todo-form\\\">\n      <input type=\\\"text\\\" id=\\\"todo-input\\\" placeholder=\\\"Add a task\\\" required>\n      <button type=\\\"submit\\\">Add</button>\n    </form>\n    <ul id=\\\"todo-list\\\"></ul>\n  </div>\n  <script src=\\\"app.js\\\"></script>\n</body>\n</html>\n",
            "app.js": "const form = document.getElementById('todo-form');\nconst input = document.getElementById('todo-input');\nconst list = document.getElementById('todo-list');\n\nlet todos = JSON.parse(localStorage.getItem('todos') || '[]');\n\nfunction render() {\n  list.innerHTML = '';\n  todos.forEach((todo, index) => {\n    const li = document.createElement('li');\n    li.textContent = todo;\n    const remove = document.createElement('button');\n    remove.textContent = 'Remove';\n    remove.addEventListener('click', () => {\n      todos.splice(index, 1);\n      save();\n    });\n    li.appendChild(remove);\n    list.appendChild(li);\n  });\n}\n\nfunction save() {\n  localStorage.setItem('todos', JSON.stringify(todos));\n  render();\n}\n\nform.addEventListener('submit', (e) => {\n  e.preventDefault();\n  todos.push(input.value);\n  input.value = '';\n  save();\n});\n\nrender();\n",
            "styles.css": "body {\n  font-family: system-ui, sans-serif;\n  background: #f8fafc;\n  color: #0f172a;\n  display: flex;\n  justify-content: center;\n  padding: 2rem;\n}\n\n.app {\n  background: white;\n  padding: 2rem;\n  border-radius: 0.5rem;\n  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);\n  width: 100%;\n  max-width: 400px;\n}\n\nform {\n  display: flex;\n  gap: 0.5rem;\n  margin: 1rem 0;\n}\n\ninput {\n  flex: 1;\n  padding: 0.5rem;\n}\n\nbutton {\n  padding: 0.5rem 1rem;\n  background: #6366f1;\n  color: white;\n  border: none;\n  border-radius: 0.25rem;\n  cursor: pointer;\n}\n\n            li {\n  display: flex;\n  justify-content: space-between;\n  padding: 0.5rem 0;\n  border-bottom: 1px solid #e2e8f0;\n}\n",
        },
    },
]


_OLD_SPLIT_COURSES: set[str] = {
    "python-beginner",
    "python-intermediate",
    "python-advanced",
    "html-beginner",
    "html-intermediate",
    "html-advanced",
    "css-beginner",
    "css-intermediate",
    "css-advanced",
    "javascript-beginner",
    "javascript-intermediate",
    "javascript-advanced",
}


async def _unpublish_old_split_courses(db: AsyncSession) -> None:
    """Hide legacy beginner/intermediate/advanced split courses from the catalog."""
    await db.execute(
        update(Course)
        .where(Course.slug.in_(_OLD_SPLIT_COURSES))
        .values(is_published=False)
    )


def _example_key_for_course(slug: str) -> str:
    mapping = {
        "typescript-essentials": "typescript",
        "react-fundamentals": "react",
        "nextjs-mastery": "nextjs",
        "fastapi-mastery": "fastapi",
        "sql-fundamentals": "sql",
        "postgresql-mastery": "postgresql",
        "docker-essentials": "docker",
        "linux-fundamentals": "linux",
        "ai-engineering": "ai",
        "machine-learning-fundamentals": "ml",
        "git-and-github": "git",
    }
    return mapping.get(slug, slug)


def _build_objectives(course_title: str, module_titles: list[str]) -> list[str]:
    first_module = module_titles[0] if module_titles else "the fundamentals"
    return [
        f"Understand core concepts and terminology in {course_title}",
        f"Apply practical skills from {first_module} through guided examples",
        f"Build real-world projects and exercises with {course_title}",
        f"Prepare for advanced topics and production-ready {course_title} work",
    ]


def _to_slug(text: str) -> str:
    return text.lower().replace(" ", "-").replace(".", "").replace("&", "and")[:50]


def _build_lesson_content(
    course_title: str,
    module_title: str,
    lesson_title: str,
    language: str,
    course_slug: str,
    lesson_index: int,
) -> dict[str, object]:
    """Return a structured lesson payload with body, code, quiz, and tips."""
    key = _example_key_for_course(course_slug)
    examples = _CODE_EXAMPLES.get(key, _CODE_EXAMPLES["python"])
    example_language, code = examples[lesson_index % len(examples)]

    body = (
        f"# {lesson_title}\n\n"
        f"In the **{course_title}** course, this lesson is part of the **{module_title}** module. "
        f"Here we explore **{lesson_title}** and see how it fits into real-world development.\n\n"
        f"## Key Takeaways\n\n"
        f"- Understand the purpose of {lesson_title.lower()}.\n"
        f"- Recognize common patterns and pitfalls.\n"
        f"- Practice with the code example below.\n\n"
        f"## Example\n\n"
        f"```{example_language}\n{code}\n```\n\n"
        f"Try modifying the example and running it yourself to reinforce what you learned."
    )

    return {
        "body": body,
        "code_language": example_language,
        "code_example": code,
        "quiz": [
            {
                "question": f"What is the main goal of {lesson_title}?",
                "options": ["Memorize syntax", "Understand and apply the concept", "Skip to the next topic"],
                "answer": "Understand and apply the concept",
            }
        ],
        "best_practices": [
            "Read the example carefully before running it",
            "Experiment by changing small parts of the code",
            "Review the key takeaways after finishing the lesson",
        ],
        "common_mistakes": [
            "Copy-pasting without understanding",
            "Ignoring error messages",
            "Skipping the practice exercise",
        ],
        "try_it": f"Modify the {lesson_title} example to solve a slightly different problem.",
    }


async def _seed_course(db: AsyncSession, course_data: dict[str, Any]) -> Course:
    modules = course_data.pop("modules")
    language = course_data["programming_language"]
    module_titles: list[str] = modules
    course = Course(
        id=uuid.uuid4(),
        **course_data,
        thumbnail=_course_thumbnail(course_data["title"]),
        estimated_duration=0,
        instructor=course_data.get("instructor", "DSir Learning Team"),
        learning_objectives=course_data.get("learning_objectives")
        or _build_objectives(course_data["title"], module_titles),
        is_published=True,
    )
    db.add(course)
    await db.flush()

    total_duration = 0
    for module_index, module_title in enumerate(modules, start=1):
        concept = Concept(
            id=uuid.uuid4(),
            course_id=course.id,
            slug=_to_slug(module_title),
            title=module_title,
            description=f"{module_title} in {course.title}. Learn through guided lessons, examples, and practice exercises.",
            order=module_index,
            prerequisites=[],
        )
        db.add(concept)
        await db.flush()

        for lesson_index in range(1, 4):
            lesson_title = f"{module_title} - Part {lesson_index}"
            duration = 15 + (lesson_index * 5)
            total_duration += duration
            lesson = Lesson(
                id=uuid.uuid4(),
                concept_id=concept.id,
                slug=f"{_to_slug(module_title)}-part-{lesson_index}",
                title=lesson_title,
                content=_build_lesson_content(
                    course.title,
                    module_title,
                    lesson_title,
                    language,
                    course_data["slug"],
                    lesson_index - 1,
                ),
                lesson_type="reading",
                position=lesson_index,
                duration_minutes=duration,
                meta={},
            )
            db.add(lesson)

    course.estimated_duration = total_duration
    return course


async def seed_courses(db: AsyncSession) -> None:
    existing_slugs = {
        row[0]
        for row in (await db.execute(select(Course.slug))).all()
    }
    for data in _COURSE_DEFINITIONS:
        if data["slug"] not in existing_slugs:
            await _seed_course(db, data)
            existing_slugs.add(data["slug"])


async def seed_projects(db: AsyncSession) -> None:
    """Seed projects linked to the matching course by slug."""
    result = await db.execute(select(Course.slug, Course.id))
    slug_to_id: dict[str, uuid.UUID] = {}
    for slug, course_id in result:
        slug_to_id[slug] = course_id

    existing_slugs = {
        row[0]
        for row in (await db.execute(select(Project.slug))).all()
    }

    for project_data in _PROJECT_DEFINITIONS:
        if project_data["slug"] in existing_slugs:
            continue
        course_id = slug_to_id.get(project_data["course_slug"])
        db.add(
            Project(
                id=uuid.uuid4(),
                course_id=course_id,
                slug=project_data["slug"],
                title=project_data["title"],
                description=project_data["description"],
                requirements=project_data["requirements"],
                starter_files=project_data["starter_files"],
                meta={"language": project_data.get("language", project_data["course_slug"].split("-")[0])},
            )
        )


async def seed_roadmap(db: AsyncSession, course_ids: list[uuid.UUID]) -> None:
    existing = await db.scalar(select(Roadmap).where(Roadmap.slug == "full-stack-developer"))
    if existing:
        return

    roadmap = Roadmap(
        id=uuid.uuid4(),
        slug="full-stack-developer",
        title="Full Stack Developer",
        description="Become a full stack developer with Python, JavaScript, and modern web technologies.",
        is_published=True,
    )
    db.add(roadmap)
    await db.flush()

    for position, course_id in enumerate(course_ids, start=1):
        db.add(RoadmapCourse(roadmap_id=roadmap.id, course_id=course_id, position=position))


async def seed_database() -> None:
    """Seed courses, projects, and roadmaps into the database."""
    logger = logging.getLogger("dsir.seed")
    async with AsyncSessionLocal() as db:
        course_count_before = await db.scalar(select(func.count(Course.id)))
        await _unpublish_old_split_courses(db)
        await seed_courses(db)
        await db.flush()

        result = await db.execute(select(Course.id))
        course_ids = [row[0] for row in result]

        await seed_projects(db)
        await seed_roadmap(db, course_ids)
        await db.commit()

        course_count_after = await db.scalar(select(func.count(Course.id)))
        logger.info("Seeding complete. Courses: %d -> %d", course_count_before or 0, course_count_after or 0)


async def _async_main() -> None:
    await seed_database()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    asyncio.run(_async_main())


if __name__ == "__main__":
    main()
