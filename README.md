# ProgressPro: Fitness Progress Analysis & Recommendation API

**ProgressPro** is a production-structured, data-driven REST API engineered to analyze an athlete's historical fitness data and deliver deterministic, explainable training and basic nutrition recommendations using predefined sports-science rules.

It is strictly a **software-only, deterministic rules engine** (no LLM wrapper, no conversational AI, no IoT/wearable dependencies) built with **Python**, **FastAPI**, **MySQL 8.0**, **SQLAlchemy 2.0**, **Pydantic v2**, and **Pytest**.

---

## 🏛 Clean Layered Architecture

ProgressPro implements the **Layered Service-Repository Pattern**, enforcing a strict unidirectional dependency graph:

```
┌────────────────────────────────────────────────────────┐
│               Client (Web, Mobile, Postman)            │
└───────────────────────────┬────────────────────────────┘
                            │ HTTP JSON / Bearer Token
┌───────────────────────────▼────────────────────────────┐
│ Presentation Layer (FastAPI Routers / Controllers)     │
│ - Request parsing & Pydantic v2 validation             │
│ - HTTP Status codes, standard error mapping            │
│ - Dependency injection (DB session, current_user)      │
└───────────────────────────┬────────────────────────────┘
                            │ DTOs / Schemas
┌───────────────────────────▼────────────────────────────┐
│ Domain / Business Logic Layer (Services)               │
│ - Workout orchestration, tracking lifecycle            │
│ - Analytics Subsystem (1RM, Tonnage, Overload, Trends) │
│ - Sports Science Rule Engine (Deterministic Advice)   │
└───────────────────────────┬────────────────────────────┘
                            │ Domain Entities / Models
┌───────────────────────────▼────────────────────────────┐
│ Data Access Layer (Repositories / CRUD)                │
│ - SQLAlchemy 2.0 type-safe queries                     │
│ - Eager loading (selectinload) to prevent N+1 issues   │
│ - Transaction boundaries (commit/rollback)             │
└───────────────────────────┬────────────────────────────┘
                            │ SQL Dialect
┌───────────────────────────▼────────────────────────────┐
│ Persistence Layer (MySQL 8.0 / InnoDB Engine)          │
│ - Foreign Keys, Constraints, Composite B-Tree Indexes  │
└────────────────────────────────────────────────────────┘
```

---

## 🛠 Technology Stack

- **Language**: Python 3.14+
- **Framework**: FastAPI (Asynchronous high-performance web framework)
- **Database**: MySQL 8.0 (InnoDB engine with UTF8MB4)
- **ORM**: SQLAlchemy 2.0 (Typed `Mapped` and `mapped_column` style)
- **Database Driver**: PyMySQL
- **Schema Validation & DTOs**: Pydantic v2 & Pydantic Settings
- **Authentication**: JWT (JSON Web Tokens via PyJWT) & Bcrypt password hashing
- **Migrations**: Alembic
- **ASGI Server**: Uvicorn
- **Testing**: Pytest with in-memory SQLite and FastAPI TestClient

---

## 📦 Core Modules (All 15 Implemented)

1. **JWT Authentication**: Secure user registration, password verification, access token (60 min) and refresh token (7 days) issuance.
2. **User Management**: Authenticated profile retrieval and updates (`GET /api/v1/users/me`, `PUT /api/v1/users/me`).
3. **Fitness Profile**: Anthropometrics, experience level, activity level, and primary goal (hypertrophy, strength, fat loss).
4. **Workout Tracking**: Hierarchical nested session logging (`Workout` $\rightarrow$ `WorkoutExercise` $\rightarrow$ `ExerciseSet`).
5. **Body-Weight History**: Daily weight and body fat percentage logs with daily uniqueness constraints.
6. **Sleep & Recovery Tracking**: Daily sleep duration, subjective quality (1-5), and resting heart rate logs.
7. **Basic Nutrition Tracking**: Daily total calories, protein, carbohydrates, fats, and water consumption.
8. **Workout Volume Analysis**: Total tonnage ($\sum w \times r$) and effective working sets mapped to muscle groups.
9. **Strength Progression Analysis**: One-Repetition Maximum (1RM) estimation via the **Epley equation** and weekly progression slope.
10. **Workout Consistency Analysis**: Adherence percentage, training frequency, and active weekly streaks.
11. **Progressive Overload Detection**: Multi-dimensional overload detection (Load increase, Rep increase, Volume increase, Plateau, Regression).
12. **Recovery Analysis**: Rolling 7-day sleep average, accumulated sleep debt, and composite 0-100 recovery score.
13. **Overall Progress Scoring**: Multi-factor weighted score (0-100) across 5 distinct pillars (Consistency 25%, Overload 30%, Volume 15%, Recovery 15%, Nutrition 15%).
14. **Explainable Fitness Recommendations**: Predefined sports-science rules (TR-001 Deload, TR-002 Volume below MEV, TR-003 Volume above MRV, TR-005 Consistency warning).
15. **Basic Rule-Based Nutrition Recommendations**: Mifflin-St Jeor BMR & TDEE calculation, ISSN protein targets (NR-001), energy balance checks (NR-002, NR-003), and hydration targets (NR-004).

---

## 🗄 Database Entities (9 Core Tables)

1. **`users`**: User identity, hashed credentials, status, and timestamps.
2. **`fitness_profiles`**: 1-to-1 demographic and baseline attributes for metabolic calculations.
3. **`exercises`**: Catalog of movements categorized by primary/secondary muscle groups and mechanics.
4. **`workouts`**: Training sessions with date, duration, and session RPE (composite index on `user_id, workout_date`).
5. **`workout_exercises`**: Junction connecting workouts to exercises, preserving movement order.
6. **`exercise_sets`**: Individual sets with load (kg), reps, RPE, and completion status.
7. **`weight_records`**: Daily weight entries (unique on `user_id, recorded_date`).
8. **`sleep_records`**: Daily sleep duration and quality entries (unique on `user_id, recorded_date`).
9. **`nutrition_records`**: Daily calories and macronutrient entries (unique on `user_id, recorded_date`).

---

## 🚀 Quickstart Guide

### 1. Set Up Virtual Environment & Dependencies
```bash
# Clone or navigate to the repository
cd ProgressPro

# Create virtual environment (Python 3)
py -m venv .venv
.\.venv\Scripts\activate   # On Windows
source .venv/bin/activate # On Linux/macOS

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` and adjust database credentials:
```bash
cp .env.example .env
```
Ensure your MySQL server is running and create the database:
```sql
CREATE DATABASE progresspro_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 3. Run Database Migrations
Apply Alembic migrations to generate all 9 tables and indexes:
```bash
alembic upgrade head
```

### 4. Seed the Database with Demo Data
Populate the exercise library, demo athlete account, and 4 weeks of training and recovery data:
```bash
python scripts/seed_data.py
```
*Demo credentials: `demo@progresspro.com` / `Password123!`*

### 5. Start the Development Server
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
Interactive API documentation and UI will be available at:
- **Sports-Science UI Dashboard**: [http://127.0.0.1:8000/ui](http://127.0.0.1:8000/ui) (or `/dashboard`)
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Health Check**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

### 6. Run the Automated Test Suite
```bash
pytest -v
```
*(All 26 automated tests run cleanly using in-memory SQLite with zero external database dependencies).*

---

## 📡 Complete API Endpoint Reference

### Authentication & Users
| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `POST` | `/api/v1/auth/register` | Register new user account | No |
| `POST` | `/api/v1/auth/login` | Login and receive Bearer JWT tokens | No |
| `POST` | `/api/v1/auth/refresh` | Exchange refresh token for fresh access token | No |
| `GET` | `/api/v1/users/me` | Fetch authenticated user profile | Yes |
| `PUT` | `/api/v1/users/me` | Update authenticated user profile | Yes |

### Fitness Profile
| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `POST` | `/api/v1/profile` | Create user fitness profile | Yes |
| `GET` | `/api/v1/profile` | Retrieve user fitness profile | Yes |
| `PUT` | `/api/v1/profile` | Update user fitness profile | Yes |

### Exercise Catalog & Workouts
| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `GET` | `/api/v1/exercises` | List exercises (category, muscle group filters) | Yes |
| `POST` | `/api/v1/exercises` | Create custom exercise | Yes |
| `GET` | `/api/v1/exercises/{id}` | Get exercise details | Yes |
| `DELETE` | `/api/v1/exercises/{id}` | Delete custom exercise | Yes |
| `POST` | `/api/v1/workouts` | Log nested workout session (exercises + sets) | Yes |
| `GET` | `/api/v1/workouts` | List workouts with date range and pagination | Yes |
| `GET` | `/api/v1/workouts/{id}` | Get full workout details with nested sets | Yes |
| `PUT` | `/api/v1/workouts/{id}` | Update workout metadata | Yes |
| `DELETE` | `/api/v1/workouts/{id}` | Delete workout session and cascade delete sets | Yes |

### Daily Tracking (Weight, Sleep, Nutrition)
| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `POST` | `/api/v1/tracking/weight` | Log daily body weight & body fat | Yes |
| `GET` | `/api/v1/tracking/weight` | Get weight history | Yes |
| `PUT` | `/api/v1/tracking/weight/{id}` | Update weight log entry | Yes |
| `DELETE` | `/api/v1/tracking/weight/{id}` | Delete weight log entry | Yes |
| `POST` | `/api/v1/tracking/sleep` | Log daily sleep duration & quality (1-5) | Yes |
| `GET` | `/api/v1/tracking/sleep` | Get sleep history | Yes |
| `PUT` | `/api/v1/tracking/sleep/{id}` | Update sleep log entry | Yes |
| `DELETE` | `/api/v1/tracking/sleep/{id}` | Delete sleep log entry | Yes |
| `POST` | `/api/v1/tracking/nutrition` | Log daily calories & macros (P/C/F/Water) | Yes |
| `GET` | `/api/v1/tracking/nutrition` | Get nutrition history | Yes |
| `PUT` | `/api/v1/tracking/nutrition/{id}` | Update nutrition log entry | Yes |
| `DELETE` | `/api/v1/tracking/nutrition/{id}` | Delete nutrition log entry | Yes |

### Mathematical Analytics
| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `GET` | `/api/v1/analytics/volume` | Volume tonnage & MEV/MAV/MRV landmark classification | Yes |
| `GET` | `/api/v1/analytics/strength` | Epley 1RM progression and weekly trend slope | Yes |
| `GET` | `/api/v1/analytics/consistency` | Training frequency, adherence %, and active streaks | Yes |
| `GET` | `/api/v1/analytics/progressive-overload` | Load, rep, and volume progressive overload detection | Yes |
| `GET` | `/api/v1/analytics/recovery` | Sleep debt and 0-100 recovery readiness score | Yes |
| `GET` | `/api/v1/analytics/progress-score` | Weighted composite 0-100 overall progress score | Yes |

### Explainable Recommendations
| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `GET` | `/api/v1/recommendations/fitness` | Explainable training adjustments (Deload, Volume) | Yes |
| `GET` | `/api/v1/recommendations/nutrition` | Explainable protein, calorie, and hydration targets | Yes |
| `GET` | `/api/v1/recommendations/report` | Unified audit report combining score and all advice | Yes |

---

## 🧪 Sports-Science Rules Matrix

| Rule ID | Name | Trigger Condition | Sports Science Rationale | Actionable Guidance |
|---|---|---|---|---|
| **TR-001** | Deload Week Recommended | 7-day Recovery Score $< 55$ AND $\ge 3$ high RPE ($\ge 8.5$) sessions | Sustained CNS fatigue elevates injury risk and blunts muscle protein synthesis. | Reduce volume by 40-50% and load by 10-15% for 1 week. |
| **TR-002** | Volume Below MEV | Muscle group effective sets $< 10$ sets/week | Volume below Minimum Effective Volume is insufficient for optimal hypertrophy. | Add 2-3 working sets per week for target muscle group. |
| **TR-003** | Volume Exceeding MRV | Muscle group effective sets $> 20$ sets/week | Exceeding Maximum Recoverable Volume generates junk fatigue without additional growth. | Reduce volume to 12-16 sets (MAV range). |
| **TR-005** | Low Consistency | 30-day workout adherence $< 60\%$ | Consistency is the prerequisite for progressive neuromuscular adaptation. | Switch to an achievable 3-day Full Body split until streak is restored. |
| **NR-001** | Protein Target Deficit | 7-day average protein $< 85\%$ of target ($1.8\text{ g/kg}$ hypertrophy / $2.2\text{ g/kg}$ fat loss) | Inadequate amino acid substrate blunts muscle protein synthesis. | Increase daily protein intake by calculated deficit grams. |
| **NR-002** | Caloric Deficit in Hypertrophy | Goal is `hypertrophy` AND calories $< \text{TDEE} - 100\text{ kcal}$ | Muscle tissue accretion in trained athletes is suboptimal in an energy deficit. | Increase intake into a lean surplus ($+250\text{ to }350\text{ kcal/day}$). |
| **NR-003** | Excessive Caloric Deficit | Goal is `fat_loss` AND calories $< \text{TDEE} - 800\text{ kcal}$ | Excessive energy deficits accelerate lean muscle catabolism and metabolic slowdown. | Moderate deficit to $400-500\text{ kcal}$ below TDEE. |
| **NR-004** | Hydration Target | Average water $< 75\%$ of target ($35\text{ mL/kg}$) | Mild dehydration decreases peak force production and elevates perceived exertion. | Aim for calculated daily Liters of water. |
