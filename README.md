# EXTRACT // 01 -- Meeting Action Item Extractor

A minimalist, high-throughput meeting intelligence engine that transforms messy, unstructured meeting transcripts and dialogue into strictly typed, deterministic JSON payloads.

Designed with a Notion and Vercel technical editorial aesthetic, the system couples an asynchronous Python backend running on FastAPI and Pydantic v2 with an ultra-responsive Vue 3 (Composition API) and Tailwind CSS single-page workspace. Accelerated by Groq hardware inference using `qwen/qwen3.8-27b` in Strict JSON Mode.

---

## Overview & Architecture

Modern product, engineering, and leadership teams produce hours of spoken dialogue and sprawling raw notes every week. Extracting consensus, critical operational pivots, and task assignments is traditionally error-prone and slow.

`EXTRACT // 01` replaces ambiguous LLM chat outputs with an industrial API pipeline guaranteeing schema conformance:

```
[ Raw Meeting Transcript ]
           |
           v
[ FastAPI REST Ingestion ]
           |  (Pydantic v2: MeetingInput)
           v
[ Groq LPU Inference Engine ]
           |  (qwen/qwen3.8-27b | json_object mode)
           v
[ Pydantic v2 Output Validation ]
           |  (Enforces MeetingOutput data contract)
           v
[ Vue 3 Utilitarian Workspace ]
   ├── Concise Summary
   ├── Key Decisions (Sharp square markers)
   └── Action Items Matrix (Task, Owner, Deadline)
```

### Core Design Principles

- **Strictly Monochrome Aesthetic**: Pure white background (`#FFFFFF`), off-white secondary surfaces (`#FAFAFA`), crisp 1px borders (`#E5E7EB` and `#000000`), and zero emojis or decorative fluff.
- **Deterministic Contract Enforcement**: No conversational filler, Markdown artifacts, or hallucinated schemas. Guaranteed JSON matching `MeetingOutput`.
- **High Concurrency & Low Latency**: Hardware-accelerated inference over Groq LPUs delivering sub-second completions for typical sprint and post-mortem transcripts.

---

## Technical Specifications

| Parameter              | Specification                                                                  |
| ---------------------- | ------------------------------------------------------------------------------ |
| **Inference Engine**   | Qwen (`qwen/qwen3.8-27b`) via Groq Cloud API                                   |
| **Decoding Strategy**  | Strict JSON Mode (`response_format: {"type": "json_object"}`)                  |
| **Token Limit**        | 2,048 max completion tokens (`max_completion_tokens: 2048`)                    |
| **Validation Layer**   | Pydantic v2 Schema Enforcement (`MeetingInput`, `ActionItem`, `MeetingOutput`) |
| **Backend Framework**  | FastAPI (Python 3.11+) asynchronous REST service                               |
| **ASGI Server**        | Uvicorn with CORSMiddleware enabled                                            |
| **Frontend Framework** | Vue 3 (Composition API, `<script setup>`) + Vite                               |
| **Styling**            | Tailwind CSS with custom monochrome typography palette                         |
| **Icons**              | `lucide-vue-next` (functional UI indicators only)                              |
| **Typography**         | `Inter` (prose / headings) paired with `JetBrains Mono` (code / metadata)      |

---

## REST API Specification

### Endpoint: `POST /extract`

Consumes a raw transcript and returns a structured breakdown.

#### Request Schema (`MeetingInput`)

```json
{
  "transcript": "string (raw dialogue, meeting notes, or multi-speaker transcript)"
}
```

#### Response Schema (`MeetingOutput`)

```json
{
  "meeting_summary": "High-level paragraph summarizing primary themes and sync outcomes.",
  "key_decisions": [
    "Formal architectural decision or deferred roadmap milestone",
    "Agreed operational standard or protocol change"
  ],
  "action_items": [
    {
      "task": "Specific actionable deliverable",
      "owner": "Assignee name or 'Unassigned'",
      "deadline": "ISO date, day of week, or 'TBD'"
    }
  ]
}
```

### Endpoint: `GET /health`

Health check verification endpoint.

```json
{
  "status": "ok"
}
```

---

## Project Structure

```
Meeting-Action-extractor/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application, CORS middleware, Groq handler
│   └── schema.py            # Pydantic v2 data models (MeetingInput, ActionItem, MeetingOutput)
├── frontend/
│   ├── index.html           # Single-page HTML shell with Inter & JetBrains Mono fonts
│   ├── package.json         # Vue 3, Vite, Tailwind CSS, Lucide icons dependencies
│   ├── postcss.config.js    # PostCSS pipeline configuration
│   ├── tailwind.config.js   # Monochrome utility palette configuration
│   ├── vite.config.js       # Vite build setup
│   └── src/
│       ├── App.vue          # Full vertical flow (Nav, Hero, Workspace, Spec, Footer)
│       ├── main.js          # Vue 3 entrypoint
│       └── style.css        # Tailwind base directives and custom monospace scrollbar
├── .env                     # Groq API key configuration
├── .gitignore
└── README.md                # Project documentation
```

---

## Getting Started

### Prerequisites

- **Python 3.11+**
- **Node.js 18+** and **npm**
- **Groq API Key** (obtainable from [Groq Console](https://console.groq.com/))

### 1. Environment Setup

Create or verify the `.env` file in the project root:

```bash
GROQ_API_KEY=gsk_your_groq_api_key_here
```

### 2. Backend Setup & Run

Install Python dependencies:

```bash
pip install fastapi uvicorn groq python-dotenv pydantic
```

Start the FastAPI application with Uvicorn:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`. You can inspect the interactive OpenAPI documentation at `http://localhost:8000/docs`.

### 3. Frontend Setup & Run

In a separate terminal, navigate to the `frontend` directory and install dependencies:

```bash
cd frontend
npm install
```

Start the Vite development server:

```bash
npm run dev
```

Open `http://localhost:5173` in your browser.

To create an optimized production build:

```bash
npm run build
```

---

## User Experience & Interactive Features

1. **Top Editorial Navigation**: Minimal brand mark (`EXTRACT // 01`), anchor navigation (`Architecture`, `API Spec`), and a `Launch Workspace` jump link.
2. **Preset Transcripts**:
   - **Sample 1 (Sprint Planning)**: Simulates an engineering sync addressing database connection pool scaling, customer migration holds, frontend token refresh edge cases, and AWS KMS integration.
   - **Sample 2 (Post-Mortem)**: Simulates an infrastructure incident review analyzing a cache eviction storm, Redis CPU saturation, circuit breakers, and SLA remediation items.
3. **Live Metrics**: Monospace character and word count tracking updating in real time as the user types or edits raw notes.
4. **Structured Presentation**:
   - Executive **Summary** paragraph.
   - **Key Decisions** displayed with square bullet markers.
   - **Action Items Matrix** with distinct task labels, bordered owner tags, and deadline stamps.
5. **One-Click JSON Export**: Copies the validated data payload directly to the clipboard with visual confirmation feedback.