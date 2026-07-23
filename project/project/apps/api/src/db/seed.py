import asyncio
import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import AsyncSessionLocal
from src.models.content import Concept, Course, Lesson, Roadmap, RoadmapCourse


_CODE_EXAMPLES: dict[str, list[tuple[str, str]]] = {
    "Python": [
        ("python", "# Variables and data types\nname = 'Alice'\nage = 30\nprint(f'{name} is {age}')"),
        ("python", "# Conditional logic\nscore = 85\nif score >= 80:\n    print('Great job!')"),
        ("python", "# List comprehension\nsquares = [x**2 for x in range(10)]\nprint(squares)"),
        ("python", "# Dictionary usage\nuser = {'name': 'Alice', 'role': 'admin'}\nprint(user.get('role'))"),
        ("python", "# Function definition\ndef greet(name):\n    return f'Hello, {name}'\nprint(greet('DSir'))"),
    ],
    "HTML/CSS": [
        ("html", "<h1>Hello World</h1>\n<p>Welcome to DSir.</p>"),
        ("css", "body {\n  background: #f8fafc;\n  color: #0f172a;\n}"),
        ("html", "<button class='btn'>Click me</button>"),
        ("css", ".btn {\n  padding: 0.5rem 1rem;\n  border-radius: 0.375rem;\n}"),
    ],
    "JavaScript": [
        ("javascript", "const greeting = 'Hello DSir';\nconsole.log(greeting);"),
        ("javascript", "const nums = [1, 2, 3];\nconst doubled = nums.map(n => n * 2);"),
        ("javascript", "async function fetchData() {\n  const res = await fetch('/api/data');\n  return res.json();\n}"),
        ("javascript", "document.querySelector('#btn').addEventListener('click', () => {\n  console.log('clicked');\n});"),
    ],
    "TypeScript": [
        ("typescript", "type User = {\n  id: string;\n  email: string;\n};\nconst u: User = { id: '1', email: 'a@b.com' };"),
        ("typescript", "function add(a: number, b: number): number {\n  return a + b;\n}"),
        ("typescript", "interface Course {\n  title: string;\n  duration: number;\n}"),
    ],
    "React": [
        ("tsx", "function Welcome({ name }: { name: string }) {\n  return <h1>Hello, {name}</h1>;\n}"),
        ("tsx", "const [count, setCount] = useState(0);"),
        ("tsx", "useEffect(() => {\n  console.log('mounted');\n}, []);"),
    ],
    "Next.js": [
        ("tsx", "export default function Page() {\n  return <h1>My Page</h1>;\n}"),
        ("tsx", "export async function generateStaticParams() {\n  return [{ id: '1' }];\n}"),
        ("typescript", "export const revalidate = 60;"),
    ],
    "FastAPI": [
        ("python", "from fastapi import FastAPI\napp = FastAPI()\n\n@app.get('/')\ndef read_root():\n    return {'ok': True}"),
        ("python", "from pydantic import BaseModel\nclass Item(BaseModel):\n    name: str\n    price: float"),
        ("python", "@app.get('/items/{item_id}')\ndef read_item(item_id: int):\n    return {'item_id': item_id}"),
    ],
    "SQL": [
        ("sql", "SELECT id, title FROM courses WHERE is_published = true;"),
        ("sql", "SELECT c.title, COUNT(l.id) FROM courses c\nJOIN lessons l ON l.course_id = c.id\nGROUP BY c.title;"),
        ("sql", "INSERT INTO users (email) VALUES ('alice@example.com');"),
    ],
    "PostgreSQL": [
        ("sql", "CREATE TABLE users (\n  id UUID PRIMARY KEY,\n  email TEXT NOT NULL\n);"),
        ("sql", "CREATE INDEX idx_users_email ON users(email);"),
        ("sql", "SELECT * FROM users WHERE email ILIKE '%@example.com';"),
    ],
    "Docker": [
        ("dockerfile", "FROM python:3.11-slim\nWORKDIR /app\nCOPY . .\nCMD ['python', 'app.py']"),
        ("bash", "docker build -t dsir-api .\ndocker run -p 8000:8000 dsir-api"),
        ("yaml", "version: '3.9'\nservices:\n  app:\n    image: dsir-api"),
    ],
    "Linux": [
        ("bash", "ls -la /var/log\ncd /home/user"),
        ("bash", "chmod +x script.sh\n./script.sh"),
        ("bash", "sudo systemctl restart nginx"),
    ],
    "AI Engineering": [
        ("python", "from openai import OpenAI\nclient = OpenAI()\nresponse = client.chat.completions.create(\n    model='gpt-4o',\n    messages=[{'role': 'user', 'content': 'Hello'}]\n)"),
        ("python", "# Prompt template\nprompt = f'Answer as an expert: {question}'"),
        ("python", "# RAG retrieval\nchunks = vector_store.similarity_search(query, k=5)"),
    ],
    "Machine Learning": [
        ("python", "from sklearn.linear_model import LinearRegression\nmodel = LinearRegression()\nmodel.fit(X, y)"),
        ("python", "from sklearn.model_selection import train_test_split\nX_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)"),
        ("python", "import pandas as pd\ndf = pd.read_csv('data.csv')\nprint(df.head())"),
    ],
    "Git": [
        ("bash", "git init\ngit add .\ngit commit -m 'initial commit'"),
        ("bash", "git checkout -b feature/new-ui\ngit push -u origin feature/new-ui"),
        ("bash", "git pull origin main --rebase"),
    ],
}


_COURSE_DEFINITIONS: list[dict[str, Any]] = [
    {
        "slug": "python-fundamentals",
        "title": "Python Fundamentals",
        "description": "Master Python from the ground up. Learn syntax, data structures, functions, object-oriented programming, and build real projects.",
        "category": "Backend",
        "programming_language": "Python",
        "technology": "Python",
        "difficulty": "beginner",
        "thumbnail": "https://images.unsplash.com/photo-1526379095098-d400fd843cea?w=800&auto=format&fit=crop",
        "skills": ["Python", "Variables", "Control Flow", "Functions", "OOP Basics"],
        "modules": ["Getting Started", "Data Structures", "Control Flow & Functions", "Object-Oriented Programming"],
    },
    {
        "slug": "advanced-python",
        "title": "Advanced Python",
        "description": "Dive deeper into decorators, generators, concurrency, metaclasses, and performance optimization in Python.",
        "category": "Backend",
        "programming_language": "Python",
        "technology": "Python",
        "difficulty": "advanced",
        "thumbnail": "https://images.unsplash.com/photo-1555066931-43669f2e7f2a?w=800&auto=format&fit=crop",
        "skills": ["Decorators", "Generators", "Asyncio", "Metaclasses", "Performance"],
        "modules": ["Decorators & Context Managers", "Iterators & Generators", "Concurrency", "Metaprogramming"],
    },
    {
        "slug": "git-and-github",
        "title": "Git & GitHub",
        "description": "Learn version control with Git and collaborate effectively using GitHub.",
        "category": "DevOps",
        "programming_language": "Git",
        "technology": "Git",
        "difficulty": "beginner",
        "thumbnail": "https://images.unsplash.com/photo-1618401471353-b98afee0b2fe?w=800&auto=format&fit=crop",
        "skills": ["Git", "GitHub", "Branching", "Merging", "Pull Requests"],
        "modules": ["Version Control Basics", "Branching & Merging", "Collaboration", "Advanced Git"],
    },
    {
        "slug": "html-fundamentals",
        "title": "HTML Fundamentals",
        "description": "Build semantic web pages with modern HTML5.",
        "category": "Frontend",
        "programming_language": "HTML/CSS",
        "technology": "HTML",
        "difficulty": "beginner",
        "thumbnail": "https://images.unsplash.com/photo-1621839673705-661705edf509?w=800&auto=format&fit=crop",
        "skills": ["HTML5", "Semantic Markup", "Forms", "Accessibility"],
        "modules": ["HTML Basics", "Forms & Inputs", "Semantic HTML", "Accessibility"],
    },
    {
        "slug": "css-mastery",
        "title": "CSS Mastery",
        "description": "Style beautiful, responsive websites with CSS3, Flexbox, Grid, and modern techniques.",
        "category": "Frontend",
        "programming_language": "HTML/CSS",
        "technology": "CSS",
        "difficulty": "beginner",
        "thumbnail": "https://images.unsplash.com/photo-1507721999472-758ed6d558b5?w=800&auto=format&fit=crop",
        "skills": ["CSS3", "Flexbox", "Grid", "Responsive Design", "Animations"],
        "modules": ["Selectors & the Box Model", "Flexbox", "Grid Layout", "Responsive Design"],
    },
    {
        "slug": "javascript-fundamentals",
        "title": "JavaScript Fundamentals",
        "description": "Learn modern JavaScript from variables to async programming.",
        "category": "Frontend",
        "programming_language": "JavaScript",
        "technology": "JavaScript",
        "difficulty": "beginner",
        "thumbnail": "https://images.unsplash.com/photo-1579468118864-1b9ea3c0db4b?w=800&auto=format&fit=crop",
        "skills": ["JavaScript", "ES6+", "DOM", "Async/Await", "Fetch"],
        "modules": ["Variables & Types", "Functions & Scope", "DOM Manipulation", "Asynchronous JS"],
    },
    {
        "slug": "typescript-essentials",
        "title": "TypeScript Essentials",
        "description": "Add static typing to your JavaScript projects with TypeScript.",
        "category": "Frontend",
        "programming_language": "TypeScript",
        "technology": "TypeScript",
        "difficulty": "intermediate",
        "thumbnail": "https://images.unsplash.com/photo-1516116213044-8e1b59f4a333?w=800&auto=format&fit=crop",
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
        "thumbnail": "https://images.unsplash.com/photo-1633356122544-f134324a6cee?w=800&auto=format&fit=crop",
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
        "thumbnail": "https://images.unsplash.com/photo-1517694712202-14d9537d8fa7?w=800&auto=format&fit=crop",
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
        "thumbnail": "https://images.unsplash.com/photo-1555949963-ff6271ac2b2a?w=800&auto=format&fit=crop",
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
        "thumbnail": "https://images.unsplash.com/photo-1544383835-bda4e3a9d4d5?w=800&auto=format&fit=crop",
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
        "thumbnail": "https://images.unsplash.com/photo-1558494949-efc5278e9e4a?w=800&auto=format&fit=crop",
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
        "thumbnail": "https://images.unsplash.com/photo-1605745341112-85968b19330b?w=800&auto=format&fit=crop",
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
        "thumbnail": "https://images.unsplash.com/photo-1516251193000-18f0d5a583a5?w=800&auto=format&fit=crop",
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
        "thumbnail": "https://images.unsplash.com/photo-1677442136019-21780ecbd0ac?w=800&auto=format&fit=crop",
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
        "thumbnail": "https://images.unsplash.com/photo-1551288049-b40f3aef5d76?w=800&auto=format&fit=crop",
        "skills": ["ML", "Scikit-Learn", "Pandas", "Regression", "Classification"],
        "modules": ["ML Workflow", "Regression", "Classification", "Model Evaluation"],
    },
]


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


def _build_lesson_body(
    course_title: str,
    module_title: str,
    lesson_title: str,
    language: str,
    lesson_index: int,
) -> str:
    examples = _CODE_EXAMPLES.get(language, _CODE_EXAMPLES["Python"])
    _, code = examples[lesson_index % len(examples)]
    return (
        f"# {lesson_title}\n\n"
        f"In the **{course_title}** course, this lesson is part of the **{module_title}** module. "
        f"Here we explore **{lesson_title}** and see how it fits into real-world development.\n\n"
        f"## Key Takeaways\n\n"
        f"- Understand the purpose of {lesson_title.lower()}.\n"
        f"- Recognize common patterns and pitfalls.\n"
        f"- Practice with the code example below.\n\n"
        f"## Example\n\n"
        f"```{language}\n{code}\n```\n\n"
        f"Try modifying the example and running it yourself to reinforce what you learned."
    )


def _build_module_description(module_title: str, course_title: str) -> str:
    return f"{module_title} in {course_title}. Learn through guided lessons, examples, and practice exercises."


def _seed_course(db: AsyncSession, course_data: dict[str, Any]) -> Course:
    modules = course_data.pop("modules")
    language = course_data["programming_language"]
    module_titles: list[str] = modules
    course = Course(
        id=uuid.uuid4(),
        **course_data,
        estimated_duration=0,
        instructor=course_data.get("instructor", "DSir Learning Team"),
        learning_objectives=course_data.get("learning_objectives") or _build_objectives(course_data["title"], module_titles),
        is_published=True,
    )
    db.add(course)
    db.flush()

    total_duration = 0
    for module_index, module_title in enumerate(modules, start=1):
        concept = Concept(
            id=uuid.uuid4(),
            course_id=course.id,
            slug=_to_slug(module_title),
            title=module_title,
            description=_build_module_description(module_title, course.title),
            order=module_index,
            prerequisites=[],
        )
        db.add(concept)
        db.flush()

        for lesson_index in range(1, 4):
            lesson_title = f"{module_title} - Part {lesson_index}"
            duration = 15 + (lesson_index * 5)
            total_duration += duration
            lesson = Lesson(
                id=uuid.uuid4(),
                concept_id=concept.id,
                slug=f"{_to_slug(module_title)}-part-{lesson_index}",
                title=lesson_title,
                content={
                    "body": _build_lesson_body(
                        course.title,
                        module_title,
                        lesson_title,
                        language,
                        lesson_index - 1,
                    )
                },
                lesson_type="reading",
                position=lesson_index,
                duration_minutes=duration,
                meta={},
            )
            db.add(lesson)

    course.estimated_duration = total_duration
    return course


async def seed_courses(db: AsyncSession) -> None:
    for data in _COURSE_DEFINITIONS:
        await _seed_course(db, data)


async def seed_roadmap(db: AsyncSession, course_ids: list[uuid.UUID]) -> None:
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


async def main() -> None:
    async with AsyncSessionLocal() as db:
        await seed_courses(db)
        await db.commit()


if __name__ == "__main__":
    asyncio.run(main())
