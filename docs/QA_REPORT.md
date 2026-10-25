# DSir Curriculum & Platform QA Report

**Date:** 2026-10-24
**Scope:** authored Python curriculum, learning flows, practice workspace, quiz
integrity, responsive layout, and deploy documentation.

## 1. Outcome

The platform now ships a complete, original Python curriculum and the learning
flows needed to use it end to end. The practice sandbox was split into two clear
paths: graded exercises and an independent saved-snippet workspace. Quiz answer
keys no longer reach the browser before submission, exercise reference solutions
are gated behind an attempt, and previously exposed session checks no longer
count against the login rate limit.

The legacy `python` course remains in the database as **archived**; its rich
foundation module was moved into the canonical course so existing lesson IDs and
learner progress survive. Nothing user-facing was deleted.

## 2. Curriculum delivered

| Content | Count | Notes |
|---|---:|---|
| Course | 1 | `python-programming` — Python Programming: Zero to Job-Ready |
| Modules | 20 | From execution model through FastAPI, shipping, and interviews |
| Lessons | 40 | Each ≥1,500 characters, with objectives and further reading |
| Exercises | 45 authored | Starter code, tests, hints, tags, reference solution |
| Module assessments | 20 | 80 questions total, explanations shown after submission |
| Projects | 12 authored | Requirements, rubric totalling 100 points, one capstone |

Sequence and references are informed by MIT OCW 6.100L, the official Python
Tutorial/documentation, python.org beginner resources, and CodeWithHarry's Python
handbook. Lesson prose, exercises, tests, and projects are original DSir material.

Seeding is idempotent and additive: `python -m app.seed_curriculum` upserts by
stable natural keys and never deletes progress, submissions, quiz attempts, or
accounts. `python -m app.seed` no longer wipes tables when it finds placeholder
content; it only seeds when the demo admin is absent.

## 3. Platform fixes

- **Quiz integrity** — `GET /quizzes/{id}` withholds `is_correct` and
  explanations. Submission returns per-question feedback, and the result history
  endpoint rebuilds feedback only for the learner's own attempt.
- **Quiz attempts and timing** — quizzes have a configurable attempt limit
  (`quizzes.max_attempts`, default 3, `NULL` = unlimited). `POST
  /quizzes/{id}/attempts` starts or resumes exactly one in-progress attempt, so
  reloading cannot reset a clock or buy extra tries. Server-side attempt states
  (`in_progress`, `submitted`, `expired`) make a timed-out attempt spend a try,
  and late submissions are rejected after a 60-second network grace window.
  Per-question seconds are reported by the client and clamped against the
  attempt's real elapsed time before storage. XP is granted only for the
  improvement over the learner's previous best (`quiz_attempts.xp_awarded`), so
  repeating or replaying a quiz cannot farm XP; a pass also counts once toward
  daily activity.
- **Exercise integrity** — `GET /practice/exercises/{id}/solution` requires at
  least one prior submission; the UI reveals the reference only after an attempt.
- **Graded Python runner** — the child process now supports the standard-library
  modules the curriculum teaches, including exceptions, `dataclasses`, `json`,
  `re`, `sqlite3` (tests only), and class definitions, while keeping a restricted
  importer, blocked `open`/`os`/`sys`/`subprocess`/dunder access, and CPU,
  memory, and file-size limits. Learner-reported scores remain ignored.
- **Saved snippets** — new `saved_snippets` table (migration `0008`), per-user
  CRUD scoped by `user_id`, and a `/practice/workspace` page with templates,
  stdin, run, save, load, and delete.
- **Rate limiting** — `/auth/me` is treated as a normal session probe instead of
  a credential attempt, so refreshing the app cannot lock a learner out.
- **Learning UI** — course progress and recently viewed endpoints, lesson
  navigation, runnable examples, quiz review, exercise solution reveal, and
  clearer loading/error/empty states.
- **Responsive fixes** — long code, tables, filters, navigation, quiz options,
  and sticky action bars no longer cause horizontal page overflow at 320–430 px.

## 4. Verification evidence

Environment: local FastAPI (`:8000`) + Next.js dev server (`:3000`) against the
project PostgreSQL database.

| Check | Result |
|---|---|
| `backend/.venv/bin/python -m pytest -q` | **79 passed**, including quiz attempt/timing rules and every exercise reference solution |
| `npx tsc --noEmit` | Passed, no errors |
| `npm run lint` | “No ESLint warnings or errors” |
| `npm run build` | Passed; 32 routes built, `/practice/workspace` included |
| Curriculum seeder run twice | Identical counts; 0 created on the second run |
| Responsive audit | 147 page/width combinations, 0 horizontal overflows; final 32-combination regression on changed pages, 0 issues |
| Browser journey: workspace | Loaded Pyodide from CDN, used “Read input” template, produced `Hi Ada, next year you will be 37.`, saved a snippet |
| Browser journey: quiz | Submitted answers, saw post-submission review, per-question times, attempt count and XP delta |
| Quiz integrity (live API + DB) | Attempt limit enforced at 3; reload resumed the same attempt; replay rejected with 409; identical retake granted 0 XP; fabricated timings clamped; expired timed attempts spent a try; legacy no-attempt submissions still graded; another learner's attempt rejected |
| Quiz UI at 1280/390 px | Attempt chip, elapsed clock, results stats (`XP earned`, `Time taken`), per-question review times, exhausted state; 0 px horizontal overflow |
| Browser journey: exercise | Submitted a binary search solution and received 100% |
| Browser journey: lesson | Opened the first authored lesson and marked it complete |

The full-suite run includes content tests that execute every reference solution
in an isolated subprocess with a 20-second timeout.

## 5. Deployment notes

- Apply `alembic upgrade head` before starting the new backend (adds
  `saved_snippets` in `0008` and quiz attempt limits/timing in `0009`).
- Run `python -m app.seed_curriculum` once after migrating, or let the Render
  start command do it.
- The browser sandbox loads pinned Pyodide `314.0.6` assets from
  `cdn.jsdelivr.net`; deployments with a Content-Security-Policy must allow that
  host in `script-src` and `connect-src`. The app does not fall back to executing
  learner Python on the server.
- `render.yaml` now uses `rootDir: backend` and runs migrations plus both seeders
  before Gunicorn.

## 6. Known limitations

- Pyodide execution depends on the learner's browser and network access to the
  pinned CDN; offline deployments must self-host those assets.
- Server-side grading is intentionally limited to Python standard-library
  exercises and is not a general-purpose code execution service.
- Responsive checks used Chromium at 320, 360, 375, 390, 430, 768, and 1280 px.
  Physical iOS/Android devices and Safari were not available in this environment.
- Per-question timing is client-reported and clamped to server-observed
  elapsed time; it is diagnostic data, not a proctoring guarantee. Clients that
  submit without starting an attempt are still graded but record no duration.
