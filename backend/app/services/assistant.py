"""In-app interview assistant: answers only from the repo's own content.

Design notes (kept deliberately boring so it is debuggable at 2am before an
interview):

* The corpus is built once, at import, from the same content modules the pages
  are rendered from. Nothing is fetched from the web and no Admiral system is
  queried.
* Retrieval is keyword scoring over small, meaningful chunks. It is not a
  vector store, but it is transparent: every answer can be traced to the
  excerpt numbers shown in the UI.
* Groq is called server-side only. The API key never reaches the browser.
* If the model call fails, the endpoint degrades to the matched excerpts
  instead of failing the whole request.
"""
from __future__ import annotations

import math
import re
from functools import lru_cache

import httpx

from app.config import settings

MAX_CONTEXT_CHARS = 11000
MAX_CHUNK_CHARS = 2600
TOP_K = 6
MAX_HISTORY_TURNS = 8
MAX_HISTORY_CHARS = 1500

_STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "but", "by", "can", "do",
    "does", "for", "from", "had", "has", "have", "how", "i", "if", "in",
    "into", "is", "it", "its", "me", "my", "of", "on", "or", "our", "should",
    "so", "that", "the", "their", "then", "there", "these", "they", "this",
    "to", "was", "we", "were", "what", "when", "where", "which", "who",
    "why", "will", "with", "would", "you", "your", "tell", "give", "about",
    "explain", "describe", "say", "answer", "question", "still", "actually",
    "really", "need", "needs", "use", "used", "using", "make", "makes",
    "work", "works", "like", "want", "know", "think", "thing", "things",
    "get", "gets", "got", "one", "two", "also", "just", "very", "much",
    "between", "difference", "differences", "vs", "versus",
}


class AssistantUnavailable(RuntimeError):
    """Raised when the assistant cannot run at all (no API key)."""


class AssistantError(RuntimeError):
    """Raised when the upstream model call fails."""


# ---------------------------------------------------------------------------
# Corpus
# ---------------------------------------------------------------------------

def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _render(value) -> str:
    """Flatten arbitrary content structures into readable, labelled text."""
    if value is None:
        return ""
    if isinstance(value, str):
        return _clean(value)
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list):
        parts = [_render(item) for item in value]
        return " • ".join(p for p in parts if p)
    if isinstance(value, dict):
        parts = []
        for key, item in value.items():
            if key in {"id", "icon", "source_ids", "correct_index"}:
                continue
            rendered = _render(item)
            if rendered:
                label = str(key).replace("_", " ")
                parts.append(f"{label}: {rendered}")
        return "; ".join(parts)
    return _clean(str(value))


def _add(chunks: list[dict], *, page: str, route: str, kind: str,
         cid: str, title: str, value) -> None:
    text = _render(value)
    if not text:
        return
    chunks.append(
        {
            "id": f"{kind}:{cid}",
            "page": page,
            "route": route,
            "kind": kind,
            "title": _clean(title),
            "text": text[:MAX_CHUNK_CHARS],
        }
    )


def _round1(chunks: list[dict]) -> None:
    from app.content import round1

    body = round1.get_round1()
    page, route, kind = "Round 1 Playbook", "/round-1", "round1"
    _add(
        chunks, page=page, route=route, kind=kind, cid="overview",
        title=f"{body['title']} — overview, process and gaps",
        value={
            "title": body["title"],
            "subtitle": body["subtitle"],
            "official_process": body["official_process"],
            "gap": body["gap"],
            "teams_notes": body["teams_notes"],
            "disclaimer": body["disclaimer"],
        },
    )
    for section in body["sections"]:
        _add(
            chunks, page=page, route=route, kind=kind, cid=section["id"],
            title=f"{section['title']} — section overview",
            value={"title": section["title"], "intro": section["intro"]},
        )
        for q in section["questions"]:
            _add(
                chunks, page=page, route=route, kind=kind, cid=q["id"],
                title=f"{section['title']} › {q['prompt']}",
                value={
                    "prompt": q["prompt"],
                    "evidence label": q["evidence"],
                    "why this is asked": q.get("why", ""),
                    "model answer": q.get("model_answer", ""),
                    "example code": q.get("code", ""),
                    "key points": q.get("key_points", ""),
                    "follow ups": q.get("follow_ups", ""),
                    "traps": q.get("traps", ""),
                    "current Admiral evidence": q.get("admiral_evidence", ""),
                },
            )
    flow = body["flow"]
    _add(
        chunks, page=page, route=route, kind=kind, cid="flow-note",
        title=f"{flow['title']} — how to use the 60 minutes",
        value={"title": flow["title"], "note": flow["note"]},
    )
    for segment in flow["segments"]:
        _add(
            chunks, page=page, route=route, kind=kind,
            cid=f"flow-{segment['minutes']}",
            title=f"60-minute flow {segment['minutes']} — {segment['title']}",
            value=segment,
        )


def _admiral(chunks: list[dict]) -> None:
    from app.content import admiral_iga

    body = admiral_iga.get_admiral()
    page, route, kind = "Admiral IGA Playbook", "/admiral-iga", "admiral"
    _add(
        chunks, page=page, route=route, kind=kind, cid="overview",
        title="Admiral IGA — role, team, sprint and disclaimer",
        value={
            "title": body["title"],
            "role": body["role"],
            "team": body["team"],
            "sprint": body["sprint"],
            "disclaimer": body["disclaimer"],
        },
    )
    for stage in body["ciam_stages"]:
        _add(
            chunks, page=page, route=route, kind=kind, cid=stage["id"],
            title=f"CIAM {stage['label']} — {stage['title']}",
            value=stage,
        )
    for domain in body["domains"]:
        _add(
            chunks, page=page, route=route, kind=kind, cid=domain["id"],
            title=f"Admiral domain — {domain['title']}",
            value=domain,
        )
    _add(
        chunks, page=page, route=route, kind=kind, cid="lifecycle",
        title=f"{body['lifecycle']['title']} — lifecycle stages",
        value=body["lifecycle"],
    )
    for q in body["questions"]:
        _add(
            chunks, page=page, route=route, kind=kind, cid=q["id"],
            title=f"Admiral interview question — {q['prompt']}",
            value=q,
        )
    _add(
        chunks, page=page, route=route, kind=kind, cid="schwab-map",
        title="Admiral evidence mapped to Schwab topics",
        value={"rows": body["schwab_map"], "sources": body["sources"]},
    )


def _resume(chunks: list[dict]) -> None:
    from app.content import resume_deep_dive

    page, route, kind = "Resume Deep Dive", "/resume", "resume"
    _add(
        chunks, page=page, route=route, kind=kind, cid="admiral-role",
        title="Current role — Admiral Group IGA SDET",
        value=resume_deep_dive.ADMIRAL_ROLE,
    )
    for q in resume_deep_dive.RESUME_QUESTIONS:
        _add(
            chunks, page=page, route=route, kind=kind, cid=q["id"],
            title=f"Resume question — {q['title']}",
            value={
                "title": q["title"],
                "category": q["category"],
                "guidance": q.get("guidance", ""),
                "star": q.get("star", ""),
                "strong answer": q.get("strong_answer", ""),
                "follow ups": q.get("follow_ups", ""),
                "current Admiral evidence": resume_deep_dive.ADMIRAL_EVIDENCE.get(
                    q["id"], ""
                ),
            },
        )


def _company(chunks: list[dict]) -> None:
    from app.content import company_profile

    profile = company_profile.COMPANY_PROFILE
    page, route, kind = "Company Brief", "/company", "company"
    for key, value in profile.items():
        _add(
            chunks, page=page, route=route, kind=kind, cid=key,
            title=f"Schwab company brief — {str(key).replace('_', ' ')}",
            value=value,
        )


def _iam(chunks: list[dict]) -> None:
    from app.content import iam_modules

    page, route, kind = "IAM Lab", "/iam-lab", "iam"
    for module in iam_modules.IAM_MODULES:
        cid = module["id"]
        _add(
            chunks, page=page, route=route, kind=kind, cid=f"{cid}-concepts",
            title=f"{module['title']} — summary, concepts and architecture",
            value={
                "title": module["title"],
                "summary": module["summary"],
                "concepts": module["concepts"],
                "architecture": module["architecture"],
            },
        )
        _add(
            chunks, page=page, route=route, kind=kind, cid=f"{cid}-questions",
            title=f"{module['title']} — interview questions and test cases",
            value={
                "interview questions": module["interview_questions"],
                "test cases": module["test_cases"],
                "quiz": module["quiz"],
            },
        )


def _scenarios(chunks: list[dict]) -> None:
    from app.content import scenarios

    page, route, kind = "Scenario Simulator", "/scenarios", "scenario"
    for scenario in scenarios.SCENARIOS:
        _add(
            chunks, page=page, route=route, kind=kind, cid=scenario["id"],
            title=f"Scenario — {scenario['title']}",
            value=scenario,
        )


def _flashcards(chunks: list[dict]) -> None:
    from app.content import flashcards

    page, route, kind = "Flashcards", "/flashcards", "flashcard"
    for index, card in enumerate(flashcards.CARDS):
        question, answer, topic = card[0], card[1], card[2]
        _add(
            chunks, page=page, route=route, kind=kind, cid=f"card-{index}",
            title=f"Flashcard ({topic}) — {question}",
            value={"topic": topic, "question": question, "answer": answer},
        )


def _mock(chunks: list[dict]) -> None:
    from app.content import mock_interview

    page, route, kind = "Mock Interview", "/mock-interview", "mock"
    for section in mock_interview.MOCK_SECTIONS:
        for q in section["questions"]:
            _add(
                chunks, page=page, route=route, kind=kind, cid=q["id"],
                title=f"Mock interview ({section['title']}) — {q['prompt']}",
                value={
                    "section": section["title"],
                    "minutes": section.get("minutes"),
                    "prompt": q["prompt"],
                    "guidance": q.get("guidance", ""),
                    "model answer": q.get("model_answer", ""),
                },
            )


def _research(chunks: list[dict]) -> None:
    from app.content import interview_research

    page, route, kind = "Mock Interview", "/mock-interview", "research"
    for source in interview_research.SOURCES:
        _add(
            chunks, page=page, route=route, kind=kind,
            cid=re.sub(r"\W+", "-", source["source"].lower()).strip("-")[:60],
            title=f"Interview research — {source['source']}",
            value=source,
        )


def _automation(chunks: list[dict]) -> None:
    from app.content import automation_lab

    page, route, kind = "Automation Lab", "/automation-lab", "automation"
    for exercise in automation_lab.EXERCISES:
        _add(
            chunks, page=page, route=route, kind=kind, cid=exercise["id"],
            title=f"Automation exercise ({exercise['tool']}) — {exercise['title']}",
            value={
                "title": exercise["title"],
                "tool": exercise["tool"],
                "difficulty": exercise["difficulty"],
                "exercise": exercise["exercise"],
                "solution": exercise.get("solution", ""),
                "explanation": exercise.get("explanation", ""),
                "follow ups": exercise.get("followups", ""),
            },
        )
    for qa in automation_lab.FRAMEWORK_ARCHITECTURE_QA:
        _add(
            chunks, page=page, route=route, kind=kind, cid=qa["id"],
            title=f"Framework architecture — {qa['question']}",
            value=qa,
        )


def _sql(chunks: list[dict]) -> None:
    from app.content import sql_challenges

    page, route, kind = "SQL Playground", "/sql-playground", "sql"
    for challenge in sql_challenges.SQL_CHALLENGES:
        _add(
            chunks, page=page, route=route, kind=kind, cid=challenge["id"],
            title=f"SQL challenge ({challenge['difficulty']}) — {challenge['title']}",
            value=challenge,
        )


def _roadmap(chunks: list[dict]) -> None:
    from app.content import roadmap

    page, route, kind = "Roadmap", "/roadmap", "roadmap"
    for day in roadmap.ROADMAP:
        _add(
            chunks, page=page, route=route, kind=kind,
            cid=str(day["day"]).lower().replace(" ", "-"),
            title=f"Study plan — {day['day']}: {day['title']}",
            value=day,
        )
    _add(
        chunks, page=page, route=route, kind=kind, cid="priority-questions",
        title="Priority interview questions",
        value=roadmap.PRIORITY_QUESTIONS,
    )
    _add(
        chunks, page="Cheat Sheet", route="/cheatsheet", kind="cheatsheet",
        cid="http-status-codes", title="HTTP status codes",
        value=roadmap.HTTP_STATUS_CODES,
    )
    for section in roadmap.CHEAT_SHEET_SECTIONS:
        _add(
            chunks, page="Cheat Sheet", route="/cheatsheet", kind="cheatsheet",
            cid=section["id"], title=f"Cheat sheet — {section['title']}",
            value=section,
        )


def _java(chunks: list[dict]) -> None:
    from app.content import java_questions

    page, route, kind = "Java Lab", "/java-lab", "java"
    for q in java_questions.JAVA_QUESTIONS:
        _add(
            chunks, page=page, route=route, kind=kind, cid=q["id"],
            title=f"Java question ({q['category']}) — {q['title']}",
            value={
                "title": q["title"],
                "category": q["category"],
                "difficulty": q["difficulty"],
                "problem": q["problem"],
                "solution": q.get("solution", ""),
                "explanation": q.get("explanation", ""),
                "time complexity": q.get("time_complexity", ""),
                "space complexity": q.get("space_complexity", ""),
                "hints": q.get("hints", ""),
                "follow ups": q.get("followups", ""),
            },
        )


@lru_cache(maxsize=1)
def corpus() -> tuple[dict, ...]:
    """Build the retrieval corpus once from the real content modules."""
    chunks: list[dict] = []
    for builder in (
        _round1,
        _admiral,
        _resume,
        _company,
        _iam,
        _scenarios,
        _flashcards,
        _mock,
        _research,
        _automation,
        _sql,
        _roadmap,
        _java,
    ):
        builder(chunks)
    return tuple(chunks)


# ---------------------------------------------------------------------------
# Retrieval
# ---------------------------------------------------------------------------

def _terms(text: str) -> list[str]:
    words = re.findall(r"[a-z0-9+#.]{2,}", text.lower())
    out: list[str] = []
    for word in words:
        word = word.strip(".")
        if len(word) < 2 or word in _STOP_WORDS:
            continue
        if word not in out:
            out.append(word)
    return out


@lru_cache(maxsize=1)
def _doc_freq() -> dict[str, int]:
    """How many chunks contain each term — the basis for IDF weighting."""
    freq: dict[str, int] = {}
    for chunk in corpus():
        haystack = (chunk["title"] + " " + chunk["text"]).lower()
        for term in _terms(chunk["title"] + " " + chunk["text"]):
            if term in haystack:
                freq[term] = freq.get(term, 0) + 1
    return freq


@lru_cache(maxsize=4096)
def _word(term: str) -> re.Pattern[str]:
    """Compile a whole-word matcher (so "race" does not match "trace")."""
    return re.compile(rf"\b{re.escape(term)}\b")


@lru_cache(maxsize=4096)
def _prefix(stem: str) -> re.Pattern[str]:
    return re.compile(rf"\b{re.escape(stem)}")


def search(question: str, page: str | None = None, limit: int = TOP_K) -> list[dict]:
    """Return the excerpts that best match the question, best first.

    Rare terms such as "leaver" must outweigh interview filler such as "test"
    or "access", so each term is weighted by inverse document frequency.
    """
    terms = _terms(question)
    if not terms:
        return []
    phrase = _clean(question.lower())
    freq = _doc_freq()
    total_chunks = max(len(corpus()), 1)
    weights = {}
    for term in terms:
        base = 1.0 + math.log((total_chunks + 1) / (freq.get(term, 0) + 1))
        # Ubiquitous words ("access", "test") must not outvote a rare, specific
        # word ("leaver", "certification") just by appearing in every chunk.
        # Damping is smooth, not a hard cutoff, so near-equal words like
        # authentication/authorization keep comparable weights.
        ubiquity = freq.get(term, 0) / total_chunks
        weights[term] = base / (1.0 + ubiquity * 3.0)
    total_weight = sum(weights.values())
    ordered = sorted(terms, key=lambda term: weights[term], reverse=True)
    top_term = ordered[0]
    scored: list[tuple[float, dict]] = []

    for chunk in corpus():
        title = chunk["title"].lower()
        text = chunk["text"].lower()
        score = 0.0
        matched_weight = 0.0
        matched: set[str] = set()
        for term in terms:
            weight = weights[term]
            in_title = bool(_word(term).search(title))
            in_text = bool(_word(term).search(text))
            if in_title:
                score += weight * 2.5
            if in_text:
                score += weight
            if in_title or in_text:
                matched.add(term)
                matched_weight += weight
            elif len(term) >= 5:
                # Prefix match helps "certifications" vs "certification".
                stem = term[: max(5, len(term) - 2)]
                if _prefix(stem).search(text):
                    score += weight * 0.5
                    matched_weight += weight * 0.5
        if score == 0:
            continue
        coverage = matched_weight / total_weight
        score += coverage * 5.0
        # A chunk that ignores the question's most specific word is unlikely
        # to be the evidence the answer needs.
        if top_term not in matched:
            score *= 0.4
        if len(phrase) > 12 and phrase in text:
            score += 3.0
        if page and chunk["route"] == page:
            score += 2.5
        # Long chunks should not win purely by length.
        score /= 1.0 + math.log10(max(len(text), 200) / 400)
        scored.append((score, chunk))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [chunk for _, chunk in scored[:limit]]


def _format_context(chunks: list[dict]) -> str:
    lines: list[str] = []
    used = 0
    for index, chunk in enumerate(chunks, start=1):
        block = (
            f"[{index}] {chunk['page'].upper()} — {chunk['title']}\n"
            f"{chunk['text']}\n"
        )
        if used + len(block) > MAX_CONTEXT_CHARS:
            break
        lines.append(block)
        used += len(block)
    return "\n".join(lines)


def _public_sources(chunks: list[dict]) -> list[dict]:
    return [
        {
            "index": index,
            "page": chunk["page"],
            "route": chunk["route"],
            "title": chunk["title"],
            "id": chunk["id"],
        }
        for index, chunk in enumerate(chunks, start=1)
    ]


# ---------------------------------------------------------------------------
# Model call
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are the SDET Interview Gym assistant for Daya Sagar.
He is preparing for a Schwab SDET (Cyber Security QA) interview and is currently
an SDET in Identity Governance and Administration at Admiral Group.

You may answer ONLY from the CONTEXT excerpts supplied in the user message.
These excerpts come from Daya's own prep repository: the Schwab Round 1
playbook, the Admiral IGA playbook, resume deep dive, company brief, IAM lab,
scenario simulator, flashcards, mock interview, automation/Java/SQL labs and
study roadmap.

Hard rules:
1. Use only the CONTEXT. Do not add outside facts, and never pretend the repo
   contains something it does not.
2. If the context does not cover the question, say plainly:
   "That isn't covered in the playbook yet." Then say what the closest covered
   topic is, if any. Do not guess or fill the gap from general knowledge.
3. Cite the excerpts you use inline as [1], [2] matching the numbers in CONTEXT.
4. Never invent metrics, percentages, user volumes, dates, ticket keys or
   employer facts. The Admiral brief has no measured numbers; do not create any.
5. Admiral material is internal evidence from Daya's own role brief. Say that
   when it matters. Never claim it was researched publicly or leaked from Schwab.
6. Predicted Schwab questions are predictions, not real interview material.
7. Answer like an interview coach: the direct answer first, then a short
   structure or bullets, then a one-line "say it like this" only if useful.
   Keep it under ~250 words unless code or SQL genuinely needs more.
8. If asked for code, give compilable Java/SQL grounded in the repo's examples
   and keep commentary brief."""


def _llm_messages(question: str, context: str, history: list[dict]) -> list[dict]:
    messages: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]
    for turn in history[-MAX_HISTORY_TURNS:]:
        role = turn.get("role")
        content = (turn.get("content") or "").strip()[:MAX_HISTORY_CHARS]
        if role in {"user", "assistant"} and content:
            messages.append({"role": role, "content": content})
    messages.append(
        {
            "role": "user",
            "content": (
                f"CONTEXT (the only source you may use):\n{context}\n\n"
                f"QUESTION:\n{question}"
            ),
        }
    )
    return messages


def _call_groq(question: str, context: str, history: list[dict]) -> str:
    payload = {
        "model": settings.groq_model,
        "temperature": 0.2,
        "max_tokens": 900,
        "messages": _llm_messages(question, context, history),
    }
    try:
        resp = httpx.post(
            f"{settings.groq_base_url.rstrip('/')}/chat/completions",
            headers={"Authorization": f"Bearer {settings.groq_api_key}"},
            json=payload,
            timeout=45,
        )
        resp.raise_for_status()
    except httpx.TimeoutException as exc:
        raise AssistantError("The assistant timed out. Try a shorter question.") from exc
    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code
        if status in {401, 403}:
            raise AssistantError(
                "Groq rejected the API key. Check GROQ_API_KEY on the server."
            ) from exc
        if status == 429:
            raise AssistantError(
                "Groq rate limit reached. Wait a moment and ask again."
            ) from exc
        raise AssistantError(
            f"Groq returned HTTP {status}. Try again in a moment."
        ) from exc
    except httpx.HTTPError as exc:
        raise AssistantError("Could not reach Groq. Check the server's connection.") from exc

    try:
        answer = resp.json()["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise AssistantError("Groq returned an unexpected response.") from exc
    if not answer:
        raise AssistantError("Groq returned an empty answer. Try again.")
    return answer


def _fallback_answer(chunks: list[dict]) -> str:
    lines = ["Groq is unavailable right now, so here are the closest playbook excerpts.", ""]
    for index, chunk in enumerate(chunks[:3], start=1):
        snippet = chunk["text"][:420].rstrip()
        if len(chunk["text"]) > 420:
            snippet += "…"
        lines.append(f"**[{index}] {chunk['page']} — {chunk['title']}**")
        lines.append(snippet)
        lines.append("")
    return "\n".join(lines).strip()


MAX_AUDIO_BYTES = 10 * 1024 * 1024

# Whisper guesses spellings from audio alone, so domain terms come back mangled
# ("leaver" -> "lever", "Saviynt" -> "Savient"). A short vocabulary prompt fixes
# most of that without changing the model.
_TRANSCRIBE_PROMPT = (
    "Interview prep questions about IAM and SDET work: Saviynt, IGA, joiner, "
    "mover, leaver, Entra ID, Active Directory, SAML, OAuth, Transmit Security, "
    "ServiceNow, Zephyr, Jira, SailPoint, RBAC, PAM, SCIM, SDET, Selenium, "
    "Playwright, pytest, Postman, API testing, SQL, Java, Python, Git, Admiral "
    "Group, Schwab, Daya Sagar."
)


def transcribe(audio: bytes, filename: str = "clip.webm",
               content_type: str = "audio/webm") -> str:
    """Transcribe a short dictation clip with Groq Whisper.

    Audio is posted once and not stored. The browser's built-in speech service
    is not involved, so this works on Chromium/Brave and behind VPNs where the
    Web Speech API fails with a "network" error.
    """
    if not settings.groq_api_key:
        raise AssistantUnavailable(
            "Dictation is not configured. Set GROQ_API_KEY on the backend."
        )
    if not audio:
        raise ValueError("The audio clip is empty.")
    if len(audio) > MAX_AUDIO_BYTES:
        raise ValueError("The audio clip is too large (max 10 MB).")

    try:
        resp = httpx.post(
            f"{settings.groq_base_url.rstrip('/')}/audio/transcriptions",
            headers={"Authorization": f"Bearer {settings.groq_api_key}"},
            files={"file": (filename, audio, content_type)},
            data={
                "model": settings.groq_whisper_model,
                "response_format": "json",
                "temperature": "0",
                "prompt": _TRANSCRIBE_PROMPT,
            },
            timeout=90,
        )
        resp.raise_for_status()
    except httpx.TimeoutException as exc:
        raise AssistantError(
            "Transcription timed out. Keep clips under 90 seconds and try again."
        ) from exc
    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code
        if status in {401, 403}:
            raise AssistantError(
                "Groq rejected the API key. Check GROQ_API_KEY on the server."
            ) from exc
        if status == 429:
            raise AssistantError(
                "Groq rate limit reached. Wait a moment and dictate again."
            ) from exc
        raise AssistantError(
            f"Groq could not transcribe that clip (HTTP {status})."
        ) from exc
    except httpx.HTTPError as exc:
        raise AssistantError(
            "Could not reach Groq for transcription. Check the server's connection."
        ) from exc

    try:
        text = (resp.json().get("text") or "").strip()
    except (AttributeError, TypeError, ValueError) as exc:
        raise AssistantError("Groq returned an unexpected transcription.") from exc
    if not text:
        raise AssistantError("No speech detected in that clip. Try again, a bit louder.")
    return text


def status() -> dict:
    return {
        "enabled": bool(settings.groq_api_key),
        "model": settings.groq_model if settings.groq_api_key else None,
        "excerpt_count": len(corpus()),
        "note": (
            "Grounded in the repo's content only. The Groq key stays server-side."
            if settings.groq_api_key
            else "GROQ_API_KEY is not set on the server, so the assistant is disabled."
        ),
    }


def ask(question: str, page: str | None = None,
        history: list[dict] | None = None) -> dict:
    """Answer a question using only the repo's content."""
    question = _clean(question)
    if not question:
        raise ValueError("Question cannot be empty.")
    if len(question) > 1000:
        raise ValueError("Question is too long (max 1000 characters).")
    if not settings.groq_api_key:
        raise AssistantUnavailable(
            "The assistant is not configured. Set GROQ_API_KEY on the backend."
        )

    chunks = search(question, page=page, limit=TOP_K)
    if not chunks:
        return {
            "answer": (
                "That isn't covered in the playbook yet, and no excerpt in the "
                "repo matched the question. Try naming the topic more directly "
                "(for example JML, certifications, SQL joins, or Java strings)."
            ),
            "sources": [],
            "model": settings.groq_model,
            "degraded": False,
            "note": "No matching repo content was found.",
        }

    context = _format_context(chunks)
    try:
        answer = _call_groq(question, context, history or [])
        degraded = False
        note = "Answered from repo content only."
    except AssistantError as exc:
        answer = _fallback_answer(chunks)
        degraded = True
        note = f"{exc} Showing matched excerpts instead."

    return {
        "answer": answer,
        "sources": _public_sources(chunks),
        "model": settings.groq_model,
        "degraded": degraded,
        "note": note,
    }
