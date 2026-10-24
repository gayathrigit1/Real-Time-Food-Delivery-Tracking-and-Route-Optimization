"""
Academic Word Document (.docx) and PowerPoint (.pptx) Generator
----------------------------------------------------------------
Generates professional academic project reports and presentation slide decks.
"""

from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, RGBColor
from pptx import Presentation
from pptx.dml.color import RGBColor as PPTXColor
from pptx.util import Inches as PPTXInches
from pptx.util import Pt as PPTXPt


def generate_word_report(output_path: Path):
    doc = Document()

    # Title & Metadata
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_title = title_p.add_run("Real-Time Food Delivery Tracking and Route optimization\n")
    run_title.bold = True
    run_title.font.size = Pt(22)
    run_title.font.color.rgb = RGBColor(30, 58, 138)

    sub_p = doc.add_paragraph()
    sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_sub = sub_p.add_run("Comprehensive Academic Project Report\nComputational Thinking, Algorithms, and Full-Stack Engineering")
    run_sub.font.size = Pt(13)
    run_sub.font.italic = True
    run_sub.font.color.rgb = RGBColor(71, 85, 105)

    doc.add_paragraph("―" * 45).alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Table of Contents Summary
    doc.add_heading("1. Executive Summary & Project Objectives", level=1)
    doc.add_paragraph(
        "Real-Time Food Delivery Tracking and Route optimization is an enterprise-grade full-stack web platform "
        "designed to model and resolve the operational challenges of modern on-demand food logistics. "
        "The system incorporates mathematical modeling, computational thinking principles, six fundamental algorithmic paradigms, "
        "concurrency models (asyncio, threading, multiprocessing), role-based security, relational database normalization, "
        "and modern single-page frontend architecture."
    )

    doc.add_heading("2. System Architecture & Technology Stack", level=1)
    doc.add_paragraph(
        "• Frontend: React 18, Vite 5, TypeScript 5, Vanilla CSS Design System with Glassmorphism.\n"
        "• Backend: Python 3.11/3.14, FastAPI REST APIs, OpenAPI/Swagger 3.0 specification.\n"
        "• Database: PostgreSQL (with async SQLite local driver), SQLAlchemy 2.0 Async ORM.\n"
        "• Security: JWT Bearer Tokens, Argon2/Bcrypt password hashing, Role-Based Access Control (RBAC).\n"
        "• Testing & Quality: Pytest, Hypothesis property-based testing, Pytest-cov (83% coverage), Ruff linter, Mypy static typing.\n"
        "• DevOps: Docker multi-stage builds, Docker Compose orchestration, GitHub Actions CI/CD pipeline."
    )

    doc.add_heading("3. Core Computational Thinking & 6 Optimization Algorithms", level=1)
    algorithms_data = [
        ("1. Greedy Agent Assignment", "O(N)", "O(N)", "Heuristic linear scan evaluating distance, active workload, and courier rating."),
        ("2. Dijkstra Shortest Path", "O((V+E) log V)", "O(V+E)", "Min-Heap priority queue on weighted road network graph for optimal route dispatch."),
        ("3. Dynamic Programming", "O(N * W)", "O(N * W)", "0/1 Knapsack formulation maximizing courier shift utility under time window constraints."),
        ("4. Backtracking", "O(N!) worst-case", "O(N)", "Constrained multi-drop tour permutation search with distance bounding and deadline pruning."),
        ("5. Branch and Bound", "O(2^N * N^2)", "O(N * 2^N)", "Multi-stop Traveling Salesperson Problem (TSP) with admissible minimum outgoing edge lower bound."),
        ("6. Divide and Conquer", "O(N log N)", "O(N)", "Recursive partitioning for stream order sorting, median calculation, and statistical aggregation."),
    ]
    table = doc.add_table(rows=1, cols=4)
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = "Algorithm"
    hdr_cells[1].text = "Time Complexity"
    hdr_cells[2].text = "Space Complexity"
    hdr_cells[3].text = "Implementation & Purpose"
    for alg, tc, sc, desc in algorithms_data:
        row_cells = table.add_row().cells
        row_cells[0].text = alg
        row_cells[1].text = tc
        row_cells[2].text = sc
        row_cells[3].text = desc

    doc.add_heading("4. Concurrency & Parallelism Analysis under Python GIL", level=1)
    doc.add_paragraph(
        "• asyncio: Cooperative event loop utilizing single-threaded coroutines for non-blocking I/O (database transactions, API calls).\n"
        "• threading: Operating system native threads managed via ThreadPoolExecutor. Yields substantial throughput improvements for blocking I/O (notifications, SMS dispatches) because the GIL is released during OS sleep/socket waits.\n"
        "• multiprocessing: Independent operating system processes with dedicated memory spaces and Python interpreters via ProcessPoolExecutor. Completely bypasses the GIL to achieve true multi-core parallel speedup on CPU-bound workloads."
    )

    doc.add_heading("5. Verification, Testing & Static Quality Assurance", level=1)
    doc.add_paragraph(
        "The project includes 27 comprehensive automated test cases across unit, integration, end-to-end workflow, and Hypothesis property-based testing. "
        "The backend achieved 83% statement test coverage with 0 Ruff linting errors and 0 Mypy typing errors. "
        "Frontend TypeScript was strictly verified with Vite production build."
    )

    doc.add_heading("6. Academic Viva Voce Questions & Answers", level=1)
    doc.add_paragraph(
        "Q1: Why is Dijkstra's algorithm preferred over Bellman-Ford for city road networks?\n"
        "A1: Dijkstra runs in O((V + E) log V) with a binary heap, whereas Bellman-Ford takes O(V * E). Since physical road distances cannot be negative, Dijkstra guarantees global optimality with vastly superior performance.\n\n"
        "Q2: How does the backend prevent client-side price tampering?\n"
        "A2: The client only transmits menu item IDs and quantities. The OrderService fetches authoritative prices from the database MenuItem table and computes subtotal, tax, and delivery fee entirely server-side.\n\n"
        "Q3: How does Branch and Bound prune the TSP state-space tree?\n"
        "A3: At each partial tour node, an admissible lower bound is computed using minimum outgoing edge relaxation. If lower_bound >= current_best_tour_cost, the node and all its descendants are pruned immediately."
    )

    doc.save(str(output_path))
    print(f"Word report successfully generated at: {output_path}")


def generate_powerpoint_presentation(output_path: Path):
    prs = Presentation()
    prs.slide_width = PPTXInches(13.333)
    prs.slide_height = PPTXInches(7.5)

    blank_layout = prs.slide_layouts[6]

    slides_data = [
        ("Real-Time Food Delivery Tracking and Route Optimization", "Academic Project Defense & Technical Presentation\nComputational Thinking • Algorithms • Concurrency • Full-Stack"),
        ("1. Project Overview & Motivation", "• Modern food delivery requires real-time routing, dispatching, and order tracking.\n• Integrates 6 fundamental algorithms for heuristic, exact, and analytical optimization.\n• Full-stack architecture with React/Vite/TypeScript frontend and FastAPI/PostgreSQL backend.\n• Strict backend financial verification and Role-Based Access Control."),
        ("2. Complete End-to-End System Workflow", "• Step 1: Customer registers/logs in and browses restaurant menus.\n• Step 2: Customer places order; backend validates prices and computes tax.\n• Step 3: Restaurant receives order and marks PREPARING -> READY_FOR_PICKUP.\n• Step 4: System evaluates Greedy Assignment and calculates Dijkstra Shortest Route.\n• Step 5: Courier picks up order (DELIVERING) and completes dropoff (DELIVERED).\n• Step 6: Customer views live status and Dijkstra road telemetry map."),
        ("3. System Architecture & Technology Stack", "• Frontend: React 18, Vite 5, TypeScript 5, Glassmorphic CSS Design System.\n• Backend: FastAPI (Python 3.11+), REST APIs, Pydantic v2 schemas.\n• Database: SQLAlchemy 2.0 Async ORM with SQLite local & PostgreSQL Docker.\n• Security: JWT Bearer Tokens, Bcrypt password hashing, RBAC authorization.\n• Quality: Pytest, Hypothesis property testing, 83% Coverage, Ruff & Mypy."),
        ("4. Algorithm 1: Greedy Delivery Agent Selection", "• Purpose: Instant assignment of incoming orders to the most suitable courier.\n• Scoring: Score = (0.50 * NormDist) + (0.30 * NormLoad) - (0.20 * NormRating).\n• Complexity: O(N) Time, O(N) Space.\n• Characteristics: Fast local optimum selection; minimal dispatch latency."),
        ("5. Algorithm 2: Dijkstra Shortest Path Routing", "• Purpose: Computes minimum distance path between restaurant and customer dropoff.\n• Data Structures: Weighted Adjacency List, Min-Heap Priority Queue (heapq).\n• Complexity: O((V + E) log V) Time, O(V + E) Space.\n• Guarantee: Globally optimal route for non-negative road segments."),
        ("6. Algorithm 3: Dynamic Programming (0/1 Knapsack)", "• Purpose: Courier shift order batch selection maximizing utility under time window W.\n• Recurrence: dp[i][w] = max(dp[i-1][w], dp[i-1][w - prep_time[i]] + priority[i]).\n• Complexity: O(N * W) Time, O(N * W) Space.\n• Output: Optimal selection recovered via DP table backtracking."),
        ("7. Algorithm 4: Backtracking Constrained Tour Sequencing", "• Purpose: Explores multi-drop delivery permutations under maximum distance constraints.\n• Pruning: Prunes branches exceeding distance limit or customer deadlines.\n• Complexity: O(N!) worst case, heavily pruned in constrained operational spaces.\n• Output: All valid feasible sequences and the best tour found."),
        ("8. Algorithm 5: Branch and Bound TSP Route Optimization", "• Purpose: Round-trip delivery tour optimization returning to depot.\n• Lower Bound: Minimum outgoing edge relaxation for unvisited vertices.\n• Complexity: O(2^N * N^2) worst case, exponential but pruned via best-first priority search.\n• Output: Provably optimal round-trip tour distance."),
        ("9. Algorithm 6: Divide and Conquer Stream Analytics", "• Purpose: High-throughput stream order sorting and recursive metric aggregation.\n• Master Theorem: T(N) = 2T(N/2) + O(N) => Theta(N log N).\n• Complexity: O(N log N) Time, O(N) Space.\n• Output: Total revenue, Min, Max, exact Median, and Top-K orders."),
        ("10. Empirical Algorithm Performance Benchmarks", "• 1. Greedy: 0.19 ms (N=99 agents)\n• 2. Dijkstra: 0.06 ms (V=15, E=22 graph)\n• 3. Dynamic Programming: 1.19 ms (N=29 orders, W=120)\n• 4. Backtracking: 0.16 ms (4! permutations, 24 valid tours)\n• 5. Branch & Bound: 0.39 ms (5 stops, 20 pruned nodes)\n• 6. Divide & Conquer: 4.18 ms (1000 stream records)"),
        ("11. Concurrency Architecture & Python GIL", "• asyncio: Cooperative event loop for high-concurrency non-blocking I/O.\n• threading: OS native threads with GIL release during blocking I/O (notifications).\n• multiprocessing: Independent OS processes bypassing the GIL for CPU-bound tasks.\n• Demonstrates clear separation of I/O-bound vs CPU-bound performance characteristics."),
        ("12. Testing, Code Quality & DevOps", "• 27 Automated test cases passing with 83% backend coverage.\n• Hypothesis property-based testing for financial and graph invariants.\n• 0 Ruff linter errors, 0 Mypy static typing errors.\n• Docker multi-stage containers, Docker Compose, and GitHub Actions CI/CD."),
        ("13. Conclusion, Limitations & Future Scope", "• Successfully demonstrated computational thinking and full-stack engineering.\n• Future Enhancements: Real-time GPS websockets, Traffic API integration (OSRM).\n• Metaheuristic scalability: Genetic Algorithms and Ant Colony for N > 50 stops."),
    ]

    for title, content in slides_data:
        slide = prs.slides.add_slide(blank_layout)

        # Background banner
        shape = slide.shapes.add_shape(1, 0, 0, PPTXInches(13.333), PPTXInches(1.2))
        shape.fill.solid()
        shape.fill.fore_color.rgb = PPTXColor(15, 23, 42)
        shape.line.color.rgb = PPTXColor(59, 130, 246)

        # Title
        tx_box = slide.shapes.add_textbox(PPTXInches(0.8), PPTXInches(0.2), PPTXInches(11.7), PPTXInches(0.8))
        tf = tx_box.text_frame
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = PPTXPt(24)
        p.font.bold = True
        p.font.color.rgb = PPTXColor(248, 250, 252)

        # Content
        content_box = slide.shapes.add_textbox(PPTXInches(1.0), PPTXInches(1.8), PPTXInches(11.3), PPTXInches(5.0))
        ctf = content_box.text_frame
        ctf.word_wrap = True
        for line in content.split("\n"):
            cp = ctf.add_paragraph()
            cp.text = line
            cp.font.size = PPTXPt(18)
            cp.font.color.rgb = PPTXColor(30, 41, 59)
            cp.space_after = PPTXPt(10)

    prs.save(str(output_path))
    print(f"PowerPoint presentation successfully generated at: {output_path}")


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent.parent
    docs_dir = base_dir / "docs"
    docs_dir.mkdir(exist_ok=True)

    word_file = docs_dir / "Food_Delivery_System_Academic_Report.docx"
    pptx_file = docs_dir / "Food_Delivery_System_Presentation.pptx"

    generate_word_report(word_file)
    generate_powerpoint_presentation(pptx_file)
