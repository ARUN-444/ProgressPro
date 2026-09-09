"""
Script to generate a comprehensive, highly professional viva preparation guide PDF
for the ProgressPro project using ReportLab.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_header_footer(self, page_count):
        self.saveState()
        # Suppress on cover page
        if self._pageNumber > 1:
            # Header
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(colors.HexColor("#64748B"))
            self.drawString(36, 11 * inch - 28, "PROGRESSPRO — COMPREHENSIVE PROJECT & VIVA GUIDE")
            self.drawRightString(8.5 * inch - 36, 11 * inch - 28, "FASTAPI + ORM + HTML5/JS")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(36, 11 * inch - 32, 8.5 * inch - 36, 11 * inch - 32)

            # Footer
            self.line(36, 34, 8.5 * inch - 36, 34)
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748B"))
            self.drawString(36, 22, "Confidential — Academic & Technical Viva Reference")
            page_str = f"Page {self._pageNumber} of {page_count}"
            self.drawRightString(8.5 * inch - 36, 22, page_str)
        self.restoreState()


def build_pdf(filename):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=40,
        bottomMargin=42,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    primary_color = colors.HexColor("#0F172A")
    accent_blue = colors.HexColor("#0284C7")
    accent_cyan = colors.HexColor("#0891B2")
    dark_gray = colors.HexColor("#334155")
    light_bg = colors.HexColor("#F8FAFC")
    border_color = colors.HexColor("#E2E8F0")

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=primary_color,
        spaceAfter=4,
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#475569"),
        spaceAfter=15,
    )

    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=accent_blue,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True,
    )

    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=primary_color,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True,
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=dark_gray,
        spaceAfter=5,
    )

    bullet_style = ParagraphStyle(
        'Bullet',
        parent=body_style,
        leftIndent=12,
        bulletIndent=4,
        spaceAfter=3,
    )

    qa_q_style = ParagraphStyle(
        'QAQuestion',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#0369A1"),
        spaceBefore=6,
        spaceAfter=2,
        keepWithNext=True,
    )

    qa_a_style = ParagraphStyle(
        'QAAnswer',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#1E293B"),
        leftIndent=10,
        spaceAfter=5,
    )

    callout_style = ParagraphStyle(
        'Callout',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11.5,
        textColor=colors.HexColor("#1E293B"),
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white,
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#1E293B"),
    )

    story = []

    # -------------------------------------------------------------------------
    # Cover / Header Banner
    # -------------------------------------------------------------------------
    story.append(Paragraph("ProgressPro: Project Architecture & Viva Guide", title_style))
    story.append(Paragraph("A Software-Only Sports-Science Training & Nutrition Analytics Platform | End-to-End Technical Summary & Exam Q&A", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=accent_blue, spaceBefore=0, spaceAfter=10))

    # Meta Quick Info Table
    meta_data = [
        [
            Paragraph("<b>Author / Tech Stack:</b> FastAPI (Python 3.14), SQLAlchemy 2.0, Vanilla JS, SQLite/MySQL", table_cell_style),
            Paragraph("<b>Architecture:</b> Layered Service-Repository Pattern, RESTful API, JWT Bearer Auth", table_cell_style),
        ],
        [
            Paragraph("<b>Endpoints:</b> 26 Production Endpoints across 9 Core Modules", table_cell_style),
            Paragraph("<b>Test Suite:</b> 26 Automated Pytest Unit Tests + Live End-to-End HTTP Suite (100% Pass)", table_cell_style),
        ],
    ]
    t_meta = Table(meta_data, colWidths=[270, 270])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), light_bg),
        ('BOX', (0,0), (-1,-1), 0.5, border_color),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------------------
    # Section 1: Executive Project Summary
    # -------------------------------------------------------------------------
    story.append(Paragraph("1. Executive Project Summary & Core Mission", h1_style))
    story.append(Paragraph(
        "<b>ProgressPro</b> is a software-only, data-driven fitness intelligence platform designed to eliminate guesswork "
        "in athletic progression. Unlike generic habit trackers, ProgressPro implements deterministic sports-science equations "
        "and volume landmark frameworks to evaluate training volume (MEV, MAV, MRV), 1RM strength progression, workout consistency, "
        "progressive overload across consecutive sessions, sleep debt recovery, and personalized energy expenditure (Mifflin-St Jeor). "
        "The application is completely self-contained with no paid third-party dependencies, featuring a responsive HTML5 glassmorphic UI "
        "and a robust asynchronous Python backend.",
        body_style
    ))

    # -------------------------------------------------------------------------
    # Section 2: Architectural Layers
    # -------------------------------------------------------------------------
    story.append(Paragraph("2. Layered Architecture & Design Patterns", h1_style))
    story.append(Paragraph(
        "ProgressPro strictly enforces separation of concerns through an enterprise <b>Layered Architecture</b>:",
        body_style
    ))

    arch_data = [
        [Paragraph("<b>Layer</b>", table_header_style), Paragraph("<b>Components & Responsibilities</b>", table_header_style), Paragraph("<b>Technologies Used</b>", table_header_style)],
        [
            Paragraph("<b>Presentation (UI)</b>", table_cell_style),
            Paragraph("Single-page application (SPA) architecture with tab routing (Overview, Workouts, Daily Tracking, Analytics, Recommendations, Profile), high-DPI HTML5 canvas charts, modal forms, and JWT auto-refresh interceptors.", table_cell_style),
            Paragraph("HTML5, Vanilla CSS3 (Glassmorphism), Vanilla ES6+ JS, Canvas API", table_cell_style)
        ],
        [
            Paragraph("<b>API Routing</b>", table_cell_style),
            Paragraph("10 dedicated routers registered under <code>/api/v1</code>. Handles request deserialization, Pydantic type validation, HTTP status codes (200, 201, 400, 401, 403, 404, 409, 422), and token extraction.", table_cell_style),
            Paragraph("FastAPI, APIRouter, OAuth2PasswordBearer, Dependency Injection", table_cell_style)
        ],
        [
            Paragraph("<b>Service Layer</b>", table_cell_style),
            Paragraph("Encapsulates pure business logic, mathematical calculations (Epley, Mifflin-St Jeor), sports-science rule engines, composite progress scoring, and multi-entity transactions.", table_cell_style),
            Paragraph("Python 3.14, Domain Services (Auth, Workout, Tracking, Analytics, Recs)", table_cell_style)
        ],
        [
            Paragraph("<b>Repository Layer</b>", table_cell_style),
            Paragraph("Data access abstraction isolating database queries. Eliminates N+1 queries using SQLAlchemy 2.0 <code>selectinload</code> for deep nested relationships (Workout &rarr; Exercises &rarr; Sets).", table_cell_style),
            Paragraph("SQLAlchemy 2.0 ORM, BaseRepository[T], Generic typing", table_cell_style)
        ],
        [
            Paragraph("<b>Data Persistence</b>", table_cell_style),
            Paragraph("Relational database schema with enforced foreign key cascades, unique daily constraints, indexed timestamps, and database version migration management.", table_cell_style),
            Paragraph("SQLite (local dev) / MySQL (production PyMySQL), Alembic", table_cell_style)
        ],
    ]
    t_arch = Table(arch_data, colWidths=[85, 335, 120])
    t_arch.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('BOX', (0,0), (-1,-1), 0.5, border_color),
        ('INNERGRID', (0,0), (-1,-1), 0.5, border_color),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_bg]),
    ]))
    story.append(t_arch)
    story.append(Spacer(1, 8))

    # -------------------------------------------------------------------------
    # Section 3: Module Breakdown & Button Flows
    # -------------------------------------------------------------------------
    story.append(Paragraph("3. Core Modules, Button Flows & API Endpoints", h1_style))

    modules_data = [
        ("Authentication & Security",
         "• Register Form: Submits email, password, full_name &rarr; calls POST /api/v1/auth/register (hashes password with bcrypt).\n"
         "• Login / Quick Demo: Submits credentials &rarr; calls POST /api/v1/auth/login &rarr; returns JWT access_token (30m) and refresh_token (7d).\n"
         "• Transparent Auto-Refresh: When any API call gets a 401, ApiClient intercepts, calls POST /api/v1/auth/refresh, and retries seamlessly.\n"
         "• Sign Out Button: Clears localStorage tokens, resets UI state to Guest, toggles demo banner."),

        ("Athlete Profile",
         "• Tab switch &rarr; calls GET /api/v1/profile &rarr; populates height, target weight, birth date, gender, goal, experience, activity.\n"
         "• Save Profile Settings: Submits form &rarr; calls PUT /api/v1/profile (or POST /api/v1/profile if first time) &rarr; persists baseline."),

        ("Exercise Library & Catalog",
         "• Catalog Preload: Calls GET /api/v1/exercises?limit=100 &rarr; populates modal exercise selectors and analytics exercise dropdown.\n"
         "• Custom Exercise: Calls POST /api/v1/exercises with is_custom=True and target muscle group."),

        ("Workout Logging (3-Tier Nested Hierarchy)",
         "• Log Workout Modal: Opens interactive session builder. Athletes specify date, duration, notes, and dynamic exercise cards.\n"
         "• Dynamic Set Rows: Athletes add/remove sets with weight_kg, reps, and subjective RPE (Rating of Perceived Exertion 1-10).\n"
         "• Submit Workout: Restructures data into WorkoutCreate schema &rarr; calls POST /api/v1/workouts with nested workout_exercises and exercise_sets.\n"
         "• Workouts List View: Calls GET /api/v1/workouts?limit=20 &rarr; renders session cards with exercise breakdown, total tonnage, and Delete button."),

        ("Daily Tracking (Weight, Sleep, Nutrition)",
         "• Log Weight: Form submits recorded_date, weight_kg, body_fat_percentage &rarr; calls POST /api/v1/tracking/weight (unique per date).\n"
         "• Log Sleep: Form submits sleep_duration_hours, quality_score (1-5), resting_heart_rate &rarr; calls POST /api/v1/tracking/sleep.\n"
         "• Log Nutrition: Form submits calories, protein, carbs, fats, water &rarr; calls POST /api/v1/tracking/nutrition.\n"
         "• History Cards: Calls GET /api/v1/tracking/{weight,sleep,nutrition}?limit=5 &rarr; displays sorted chronologically descending."),

        ("Analytics Subsystem",
         "• Overall Progress Score: Calls GET /api/v1/analytics/progress-score &rarr; computes 0-100 composite score across 5 weighted pillars.\n"
         "• Volume Landmarks: Calls GET /api/v1/analytics/volume &rarr; renders HTML5 canvas bar chart classifying sets into MEV, MAV, MRV.\n"
         "• Epley 1RM Strength Curve: Calls GET /api/v1/analytics/strength/{id} &rarr; plots top-set estimated 1RM progression and calculates weekly slope.\n"
         "• Progressive Overload Detector: Calls GET /api/v1/analytics/progressive-overload/{id} &rarr; compares two most recent sessions across Load, Reps, or Volume.\n"
         "• Recovery & Sleep Debt: Calls GET /api/v1/analytics/recovery &rarr; computes 7-day sleep debt against 8h target and fatigue factors."),

        ("Sports-Science Recommendation Engine",
         "• Energy Balance: Computes Mifflin-St Jeor BMR, Physical Activity Level (PAL) TDEE, ISSN 2.0g/kg protein targets, and hydration.\n"
         "• Deterministic Rules: Calls GET /api/v1/recommendations/fitness and /nutrition. Evaluates rules TR-001 (Deload), TR-002 (Below MEV), TR-003 (Above MRV), TR-005 (Consistency), NR-001 (Calorie deficit/surplus), NR-002 (Protein sufficiency), NR-004 (Hydration).\n"
         "• Unified Audit Report: Calls GET /api/v1/recommendations/report &rarr; returns combined status, energy balance, and prioritized action prescriptions.")
    ]

    for title, desc in modules_data:
        story.append(Paragraph(f"<b>{title}</b>", h2_style))
        for line in desc.split('\n'):
            story.append(Paragraph(line, bullet_style))

    story.append(Spacer(1, 6))

    # -------------------------------------------------------------------------
    # Section 4: Mathematical Models & Scientific Foundations
    # -------------------------------------------------------------------------
    story.append(Paragraph("4. Scientific & Mathematical Foundations", h1_style))

    math_data = [
        [Paragraph("<b>Framework</b>", table_header_style), Paragraph("<b>Formula / Equation</b>", table_header_style), Paragraph("<b>Sports-Science Rationale</b>", table_header_style)],
        [
            Paragraph("<b>Epley 1RM Estimation</b>", table_cell_style),
            Paragraph("<code>1RM = Weight × (1 + Reps / 30)</code><br/>(For Reps = 1: 1RM = Weight)", table_cell_style),
            Paragraph("Standard validated formula for estimating maximum strength capacity without performing dangerous true maximal lifts.", table_cell_style)
        ],
        [
            Paragraph("<b>Mifflin-St Jeor BMR</b>", table_cell_style),
            Paragraph("<b>Men:</b> 10W + 6.25H - 5A + 5<br/><b>Women:</b> 10W + 6.25H - 5A - 161<br/>(W=kg, H=cm, A=years)", table_cell_style),
            Paragraph("Gold-standard clinical equation for estimating Basal Metabolic Rate with lowest error margin in non-obese individuals.", table_cell_style)
        ],
        [
            Paragraph("<b>TDEE Calculation</b>", table_cell_style),
            Paragraph("<code>TDEE = BMR × PAL</code><br/>PAL: Sedentary (1.20) to Extra Active (1.90)", table_cell_style),
            Paragraph("Quantifies total daily caloric turnover based on athletic lifestyle and training demands.", table_cell_style)
        ],
        [
            Paragraph("<b>Volume Landmarks (Dr. Mike Israetel)</b>", table_cell_style),
            Paragraph("• MV: Maintenance (~6 sets/wk)<br/>• MEV: Min Effective (~10-12 sets/wk)<br/>• MAV: Max Adaptive (~12-18 sets/wk)<br/>• MRV: Max Recoverable (~20-22 sets/wk)", table_cell_style),
            Paragraph("Categorizes training volume to prevent both under-stimulation (wasted effort) and systemic overreaching (junk fatigue).", table_cell_style)
        ],
        [
            Paragraph("<b>Sleep Debt & Recovery Score</b>", table_cell_style),
            Paragraph("<code>Debt = &sum; max(0, 8.0 - sleep_hours)</code><br/>Score: 55% Duration + 35% Quality + 10% Fatigue factor", table_cell_style),
            Paragraph("Quantifies systemic neurological readiness and flags high risk of central nervous system (CNS) overtraining.", table_cell_style)
        ],
        [
            Paragraph("<b>Composite Progress Score</b>", table_cell_style),
            Paragraph("25% Consistency + 30% Overload + 15% Volume + 15% Recovery + 15% Nutrition", table_cell_style),
            Paragraph("Holistic 0-100 index preventing athletes from focusing solely on weight lifted while neglecting recovery and diet.", table_cell_style)
        ],
    ]
    t_math = Table(math_data, colWidths=[100, 200, 240])
    t_math.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('BOX', (0,0), (-1,-1), 0.5, border_color),
        ('INNERGRID', (0,0), (-1,-1), 0.5, border_color),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_bg]),
    ]))
    story.append(t_math)
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------------------
    # Section 5: Bugs Identified & Fixed During Health Check
    # -------------------------------------------------------------------------
    story.append(Paragraph("5. Bugs Identified & Auto-Fixed (Stability Audit)", h1_style))

    bugs_data = [
        [Paragraph("<b>Issue Identified</b>", table_header_style), Paragraph("<b>Root Cause</b>", table_header_style), Paragraph("<b>Implemented Fix</b>", table_header_style)],
        [
            Paragraph("Daily Tracking 404 Not Found", table_cell_style),
            Paragraph("Frontend called <code>/api/v1/{weight,sleep,nutrition}</code> but backend routers had prefix <code>/tracking/{...}</code>.", table_cell_style),
            Paragraph("Updated endpoints in <code>frontend/js/api.js</code> to <code>/api/v1/tracking/{...}</code>.", table_cell_style)
        ],
        [
            Paragraph("Daily Tracking 422 Validation Errors", table_cell_style),
            Paragraph("Field name discrepancies: <code>body_fat_pct</code> vs <code>body_fat_percentage</code>; <code>sleep_hours</code> vs <code>sleep_duration_hours</code>; <code>protein_g</code> vs <code>protein</code>.", table_cell_style),
            Paragraph("Implemented client-side payload normalization in <code>api.js</code> mapping all legacy keys to exact Pydantic schema names.", table_cell_style)
        ],
        [
            Paragraph("Workout Logging 422 Failure", table_cell_style),
            Paragraph("Modal sent flat exercises with <code>sets</code>; backend <code>WorkoutCreate</code> strictly required <code>workout_exercises</code> with <code>exercise_sets</code> and non-empty <code>title</code>.", table_cell_style),
            Paragraph("Added payload transformation in <code>api.js</code> and autogenerated fallback session title from date and notes.", table_cell_style)
        ],
        [
            Paragraph("Volume Landmarks Chart Failure", table_cell_style),
            Paragraph("Canvas chart function expected key-value dictionary of muscle groups, but API returned <code>muscle_group_breakdown</code> list of objects.", table_cell_style),
            Paragraph("Transformed breakdown array into key-value map inside <code>app.js</code> before passing to <code>drawVolumeLandmarksChart</code>.", table_cell_style)
        ],
        [
            Paragraph("Undefined Exercise Dropdown Labels", table_cell_style),
            Paragraph("Frontend expected <code>ex.target_muscle_group</code>, but backend model defined <code>primary_muscle_group</code>.", table_cell_style),
            Paragraph("Added fallback <code>ex.primary_muscle_group || ex.target_muscle_group</code> in exercise selectors.", table_cell_style)
        ],
        [
            Paragraph("Stale Old Records on Daily Tracking", table_cell_style),
            Paragraph("<code>WeightRepository</code>, <code>SleepRepository</code>, <code>NutritionRepository</code> queried with <code>order_by(date.asc())</code> with limit 5, returning the 5 oldest logs.", table_cell_style),
            Paragraph("Updated repositories to sort by <code>recorded_date.desc()</code> and added <code>get_latest_by_user()</code> helper.", table_cell_style)
        ],
        [
            Paragraph("SQLite Foreign Keys Inactive", table_cell_style),
            Paragraph("SQLite disables foreign key enforcement by default unless explicitly turned on per connection.", table_cell_style),
            Paragraph("Added SQLAlchemy <code>@event.listens_for(engine, 'connect')</code> listener executing <code>PRAGMA foreign_keys=ON;</code>.", table_cell_style)
        ],
    ]
    t_bugs = Table(bugs_data, colWidths=[120, 210, 210])
    t_bugs.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('BOX', (0,0), (-1,-1), 0.5, border_color),
        ('INNERGRID', (0,0), (-1,-1), 0.5, border_color),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_bg]),
    ]))
    story.append(t_bugs)
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------------------
    # Section 6: Comprehensive Viva Questions & Answers
    # -------------------------------------------------------------------------
    story.append(Paragraph("6. Likely Viva Questions & High-Scoring Answers", h1_style))
    story.append(Paragraph("Use these concise, technically sound answers during examiner questioning:", body_style))

    viva_qa = [
        ("Q1: What is the core problem ProgressPro solves?",
         "A: It bridges the gap between logging workouts and understanding actionable progress. Generic apps merely record numbers; ProgressPro applies deterministic sports-science rules (Epley, Mifflin-St Jeor, Israetel volume landmarks) to calculate fatigue, progressive overload, sleep debt, and macro adherence automatically."),

        ("Q2: Why did you choose FastAPI over Flask or Django?",
         "A: FastAPI natively supports Python asynchronous execution (async/await), automatic Pydantic data validation with descriptive 422 error payloads, dependency injection for database sessions and auth, and auto-generated OpenAPI (Swagger) interactive documentation (/docs). Django is too heavy and monolithic for a clean REST API, while Flask lacks built-in asynchronous performance and typing validation."),

        ("Q3: How does authentication and session security work?",
         "A: User passwords are encrypted with salted one-way bcrypt hashing. On login, the server generates a signed HMAC-SHA256 JWT access token (valid 30 mins) containing the user ID subject claim, plus a secure refresh token (valid 7 days). The frontend stores tokens in localStorage and includes a Bearer header in requests. If a 401 Unauthorized occurs, an API interceptor transparently exchanges the refresh token for a new access token."),

        ("Q4: How does the system prevent N+1 query performance problems?",
         "A: In the Workout logging hierarchy, a Workout has many WorkoutExercises, each having many ExerciseSets. Querying this naively causes N+1 SELECT queries. We utilize SQLAlchemy 2.0 selectinload() eager loading options in WorkoutRepository, fetching parent workouts and all nested child entities in just two efficient queries."),

        ("Q5: Explain how Progressive Overload is detected in your code.",
         "A: OverloadDetector queries the user's two most recent completed sessions for an exercise. It compares top sets and total tonnage. If top-set weight increased with equal or greater reps &rarr; LOAD_INCREASE. If load is identical but reps increased &rarr; REP_INCREASE. If total session tonnage increased by &ge; 2.5% &rarr; VOLUME_INCREASE. Otherwise, it detects PLATEAU or REGRESSION."),

        ("Q6: How does the Volume Landmarks feature work?",
         "A: In VolumeAnalyzer, working sets (excluding warmups) over the past 7 days are aggregated per muscle group and evaluated against scientific landmarks: Below Maintenance (&lt;6 sets), Maintenance (6-9 sets), Minimum Effective Volume (MEV, 10-11 sets), Maximum Adaptive Volume (MAV, 12-18 sets, optimal hypertrophy zone), and Maximum Recoverable Volume (MRV, &gt;20 sets, leading to overtraining)."),

        ("Q7: How is the Overall Progress Score (0-100) calculated?",
         "A: It is a multi-pillar weighted composite score: 25% Consistency (workout adherence vs target frequency), 30% Progressive Overload (overload trend across exercises), 15% Volume Adequacy (proportion of muscle groups in MEV/MAV), 15% Recovery Score (sleep duration, quality, sleep debt), and 15% Nutrition Adherence (logging frequency and calorie/protein sufficiency)."),

        ("Q8: How does the Mifflin-St Jeor equation compute calorie requirements?",
         "A: BMR represents calories burned at complete rest. Men: 10×weight(kg) + 6.25×height(cm) - 5×age + 5. Women: 10×weight(kg) + 6.25×height(cm) - 5×age - 161. Total Daily Energy Expenditure (TDEE) is then calculated by multiplying BMR by the Physical Activity Level (PAL) multiplier (e.g. 1.2 for sedentary, 1.55 for moderately active)."),

        ("Q9: What is the database architecture and migration strategy?",
         "A: ProgressPro uses SQLAlchemy 2.0 declarative models with Alembic for version-controlled database schema migrations. In local development it uses SQLite with PRAGMA foreign_keys=ON; in production it switches seamlessly to MySQL via PyMySQL using the DATABASE_URL environment variable without modifying a single line of business code."),

        ("Q10: Why did you build the frontend in Vanilla JavaScript instead of React or Angular?",
         "A: To demonstrate deep mastery of core web fundamentals: DOM manipulation, asynchronous fetch APIs, canvas pixel manipulation, and custom event loops without relying on third-party abstractions. This guarantees zero build-step overhead, sub-50ms initial load times, and complete control over performance."),

        ("Q11: How do you handle database constraints and prevent duplicate entries?",
         "A: We enforce UNIQUE constraints at the database level on (user_id, recorded_date) for weight, sleep, and nutrition tables, and a UNIQUE constraint on user emails. The service layer catches duplicate attempts and raises a custom DuplicateEntityException which our global exception handler translates into an HTTP 409 Conflict response with a clean JSON payload."),

        ("Q12: How are unit and integration tests structured?",
         "A: We utilize pytest with FastAPI's TestClient and an in-memory SQLite database session fixture. Tests cover auth lifecycle, profile CRUD, nested workout logging, daily tracking uniqueness constraints, analytics calculations, sports-science recommendations, and custom repository methods (26/26 tests passing)."),

        ("Q13: What happens if an athlete has insufficient data for analysis?",
         "A: Rather than crashing with an unhandled exception, services check data thresholds (e.g., progressive overload requires at least 2 sessions). If data is lacking, the service raises an InsufficientDataException (HTTP 422) with helpful diagnostic metadata, and the frontend renders an informative callout inviting the athlete to log more sessions."),

        ("Q14: How does the Recommendation Engine work without machine learning?",
         "A: ProgressPro uses an explainable deterministic rules engine based on peer-reviewed sports science (ISSN and ACSM guidelines). ML models act as 'black boxes' prone to hallucinations and unexplainable outputs; deterministic rules guarantee that every recommendation provides an exact Rule ID, observable metric, scientific rationale, and concrete actionable prescription."),

        ("Q15: What design patterns are implemented in the project?",
         "A: 1) Layered Architecture (Presentation &rarr; Routing &rarr; Service &rarr; Repository &rarr; Database); 2) Repository Pattern (abstracting data queries); 3) Dependency Injection (FastAPI Depends for db sessions and auth); 4) Factory/Singleton Pattern (ApiClient and Database Engine); 5) Observer Pattern (DOM event listeners and canvas rendering).")
    ]

    for q, a in viva_qa:
        story.append(KeepTogether([
            Paragraph(q, qa_q_style),
            Paragraph(a, qa_a_style)
        ]))

    # Build PDF with custom NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[SUCCESS] Viva Guide PDF generated at: {filename}")

if __name__ == "__main__":
    out_path = r"c:\Users\ARUN\OneDrive\Desktop\ProgressPro\ProgressPro_Viva_Guide.pdf"
    build_pdf(out_path)
