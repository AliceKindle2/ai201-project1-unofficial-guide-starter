import os
import re
import json

# ── CONFIG ─────────────────────────────────────────────────────────────────
FILES = {
    "RateMySC.txt":       "Rate My Professor",
    "UTDgradeSc.txt":     "UTD Grades",
    "CourseBookSc.txt":   "UTD CourseBook",
    "EvaSc.txt":          "UTD UES",
    "CoursicleSC.txt":    "Coursicle",
    "NicheSc.txt":        "Niche",
    "UloopSc.txt":        "Uloop",
    "collegeduniaSc.txt": "Collegedunia",
    "AcademiaSc.txt":     "AcademicJobs RMP",
    "RedditSc.txt":       "r/utdallas",
}

INPUT_DIR  = "/mnt/user-data/uploads"
OUTPUT_DIR = "/mnt/user-data/outputs"
MIN_CHARS  = 80
MAX_CHARS  = 300

# ── NOISE PATTERNS (shared across all sources) ──────────────────────────────
NOISE_PATTERNS = [
    r"^(log in|sign in|sign up|help|skip to|back to|show more|show all|add to list|read more|report|view all).*",
    r"^(post jobs|post housing|home|jobs|housing|roommates|tutors|course notes|test prep|student loans|study abroad|more)$",
    r"^(rate|compare|jump to ratings|i'm professor|rating distribution).*",
    r"^(rate your professor now|read all \d+ reviews of|view .+ fall 2026 classes).*",
    r"^(make tiktoks for coursicle|we're paying .*)$",
    r"^(tap here to apply|coursicle rating).*",
    r"^(departments?|recent semesters? teaching|typical class size|fall 2026 classes|courses?)$",
    r"^(privacy policy|terms|terms of use|terms & conditions|cookie|© \d{4}|all rights reserved|site guidelines).*",
    r"^(copyright compliance|ca notice|do not sell|uloop is an unofficial|sitemap|contact us|careers|advertise).*",
    r"^(reddit rules|reddit, inc\.|collapse navigation|resources|explore our site|higher education news).*",
    r"^(recruiters|post a job|recruitment solutions|ai recruitment|higher ed job board|career resources|job search).*",
    r"^(higher ed rankings|associations|academic journals|about us|meet the team|excellent|trustpilot|trustscore).*",
    r"^(google|view us on google|© 2026 post my job).*",
    r"^(awesome|great|good|ok|awful)\s+\d+$",
    r"^\d+\s*$",
    r"^(quality|difficulty|helpfulness|clarity|easiness)\s*[\d.]*\s*$",
    r"^(for credit|attendance|would take again|grade|textbook|online class):\s*.*",
    r"^(lecture heavy|graded by few things|accessible outside class|group projects|tough grader|lots of homework).*",
    r"^helpful\s*$",
    r"^0\s+0\s*$",
    r"^(reviewed:|reviewed:\s*(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec).*)$",
    r"^(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d+(st|nd|rd|th)?,?\s*\d{4}.*",
    r"^similar professors\s*$",
    r"^\d+:\d+\s*$",
    r"^\d+(\.\d+)?\s*/\s*5\s*$",
    r"^\d+%\s*$",
    r"^\d+%\s*(would take again|of students).*",
    r"^\d+\.\d+\s*$",
    r"^overall quality\s*$",
    r"^(highest rated|lowest rated|overall rating|rated by \d+).*",
    r"^(level of difficulty|jump to ratings|overall quality based on).*",
    r"^(poll|grade|rating \d out of \d|based on acceptance rate).*",
    r"^(full-time retention|part-time retention|academic calendar|research funding|graduation rate|student faculty ratio).*",
    r"^(female professors|male professors|average professor salary|class size breakdown|most popular majors).*",
    r"^(african american|asian american|hispanic|international|multiracial|native american|pacific islander|unknown|white)\s+\d+%",
    r"^\d+-\d+\s+students\s*$",
    r"^(information science|psychology|graphic design)\s+\d+",
    r"^(evening degree|teacher certification|study abroad|non-traditional learning)\s*.*",
    r"^(ues|sacscoc|oisds|coursebook|orion|elearning|ues support|uloop inc\.).*",
    r"^(summer|spring|fall) \d{4}.*",
    r"^(classes begin|course evaluations|final exams|exception request|reports generated).*",
    r"\*please email",
    r"^(login to|not finding|want to submit|click the|yes, during|unfortunately|there is one caveat).*",
    r"^(need help\?|contact the web|please use the feedback form).*",
    r"^[a-z]$",
    r"^(abcdefghijklmnopqrstuvwxyz)$",
    r"^(browse by last name|professor ratings search|search by department|search by last name|refine your search).*",
    r"^found \d+ professors.*",
    r"^professor ratings near.*",
    r"^(step \d\.|utd rmp live rating|browse the list of professors|add professor|best professor comments|success stories).*",
    r"^(top-rated professors and departments|how to choose courses|student reviews and insights|impact of ratings).*",
    r"^(faculty excellence|historical rating trends|rate your professor and join|frequently asked questions).*",
    r"^(how do i rate|who are the best|how do ratings|what is the effect|are there job|how anonymous|can faculty).*",
    r"^[📝⭐🎓📈💼🔒💬🏫👩‍🎓📱🎥].*",
    r"^(amazing feedback|exceptional|good|excellent)\s*$",
    r"^(community bookmarks|useful utd links|r/utdallas rules|created sep).*",
    r"^(utdallas github|academic calendar|comet calendar|elearning enhancement|campus room availability).*",
    r"^(utd news|library room reservation|course planner)\s*.*",
    r"^\d+\.\s+(whatever|posts must|be civil|don't post|do some|don't troll|don't share|do not promote|this is not).*",
    r"^(user agreement|your privacy choices|accessibility)\s*$",
    r"^u/\w+\s*$",
    r"^\d+\s*(votes?|comments?)\s*.*",
    r"^(promoted|get the ultimate|windows\.com|learn more)\s*.*",
    # AcademicJobs-specific noise
    r"^rate \w+ \w+ now!$",
    r"^comment \(optional\)$",
    r"^select a suggestion\.\.\.$",
    r"^(are you a current student|are you a peer|submit rating)\??$",
    r"^\d+ star$",
    r"^(manages? profile|manage profile).*",
    r"^(related jobs|related conferences|trending .* research|view all jobs|view all conferences).*",
    r"^(essential|featured|premium)\s+.*",
    r"^(join the conversation!|see research|see more research|promote your research|have a story).*",
    r"^submit your research.*",
    r"^photo by .* on unsplash$",
    r"^\d+/\d+/\d{4}$",
    r"^(this comment is not public\.?)$",
    r"^5\.0$",
    r"^4/\d+/\d{4}$",
    r"^8/\d+/\d{4}$",
    r"^(jun|jul|aug|sep|oct|nov|dec|jan|feb|mar|apr|may)\s+\d+,\s+\d{4}.*",
    r"^\d+ – invalid date$",
    r"^(to be announced|view all conferences →).*",
]

COMPILED_NOISE = [re.compile(p, re.IGNORECASE) for p in NOISE_PATTERNS]


def is_noise(line: str) -> bool:
    s = line.strip()
    if not s:
        return True
    if len(s) < 4:
        return True
    if re.match(r"^[-=_*#~•·★]{2,}$", s):
        return True
    for pat in COMPILED_NOISE:
        if pat.match(s):
            return True
    return False


# ── ACADEMICJOBS EXTRACTOR ──────────────────────────────────────────────────
# Strategy: find each "About <Name>" block and extract only those paragraphs.
# Everything outside an About block (conferences, jobs, news, suggestions) is dropped.

def extract_academicjobs(raw: str) -> list[dict]:
    records = []
    # Split into professor sections on "Rate My Professor <Name>"
    sections = re.split(r"Rate My Professor\s+([A-Z][^\n]+)\n", raw)
    # sections = [preamble, name1, body1, name2, body2, ...]
    i = 1
    while i < len(sections) - 1:
        professor_name = sections[i].strip()
        body = sections[i + 1]
        i += 2

        # Within the body, find the "About <Name>" paragraph block
        about_match = re.search(
            r"About\s+\w+\s*\n(.*?)(?=RELATED JOBS|RELATED CONFERENCES|ENGINEERING JOBS|MATHEMATICS JOBS|BUSINESS|GEOSCIENCE|$)",
            body, re.DOTALL | re.IGNORECASE
        )
        if not about_match:
            continue

        about_text = about_match.group(1).strip()

        # Clean line by line — drop any remaining noise inside the About block
        lines = about_text.splitlines()
        kept = []
        for line in lines:
            line = line.strip()
            if line and not is_noise(line) and len(line) > 30:
                kept.append(line)

        clean = " ".join(kept)
        if len(clean) >= MIN_CHARS:
            records.append({
                "professor": professor_name,
                "text": clean,
            })

    return records


# ── RMP EXTRACTOR ───────────────────────────────────────────────────────────

def extract_rmp_reviews(raw: str) -> list[dict]:
    lines = [l.strip() for l in raw.splitlines()]
    records = []
    professor = None
    department = None
    course = None
    i = 0
    while i < len(lines):
        line = lines[i]
        if (i + 2 < len(lines)
                and re.match(r"^[A-Z][a-z]+([ -][A-Z][a-z]+)+$", line)
                and not re.match(r"^(The|Rate|Help|Site|Terms|Privacy|Copyright)", line)
                and lines[i+2].startswith("The University of Texas")):
            professor = line
            department = lines[i+1]
            i += 3
            continue
        if re.match(r"^[A-Z]{2,4}\s*\d{4}$", line):
            course = line
            i += 1
            continue
        if len(line) > 60 and not is_noise(line):
            records.append({
                "professor": professor,
                "department": department,
                "course": course,
                "text": line,
            })
        i += 1
    return records


# ── COURSICLE EXTRACTOR ─────────────────────────────────────────────────────

def extract_coursicle_reviews(raw: str) -> list[dict]:
    lines = [l.strip() for l in raw.splitlines()]
    records = []
    professor = None
    course = None
    i = 0
    while i < len(lines):
        line = lines[i]
        if line == "Professors at UTD" and i + 1 < len(lines):
            professor = lines[i+1].strip()
            i += 2
            continue
        course_match = re.match(r"^([A-Z]{2,4}\s*\d{4,})\s*[•·]", line)
        if course_match:
            course = course_match.group(1).strip()
            i += 1
            continue
        if len(line) > 40 and not is_noise(line):
            records.append({"professor": professor, "course": course, "text": line})
        i += 1
    return records


# ── GENERIC CLEANER ─────────────────────────────────────────────────────────

def generic_clean(raw: str) -> str:
    lines = raw.splitlines()
    kept = [l.strip() for l in lines if not is_noise(l)]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(kept)).strip()


# ── CHUNKER ─────────────────────────────────────────────────────────────────

def split_sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def chunk_text(text: str, source: str,
               professor: str = None, course: str = None) -> list[dict]:
    sentences = split_sentences(text)
    raw_chunks = []
    current = ""
    for sentence in sentences:
        if len(sentence) > MAX_CHARS:
            if current.strip():
                raw_chunks.append(current.strip())
                current = ""
            words = sentence.split()
            segment = ""
            for word in words:
                if len(segment) + len(word) + 1 <= MAX_CHARS:
                    segment = (segment + " " + word).strip()
                else:
                    if segment:
                        raw_chunks.append(segment)
                    segment = word
            if segment:
                raw_chunks.append(segment)
            continue
        proposed = (current + " " + sentence).strip()
        if len(proposed) <= MAX_CHARS:
            current = proposed
        else:
            if current.strip():
                raw_chunks.append(current.strip())
            current = sentence
    if current.strip():
        raw_chunks.append(current.strip())

    result = []
    for chunk in raw_chunks:
        if len(chunk) >= MIN_CHARS:
            entry = {
                "chunk_id": f"{source.replace(' ', '_')}_{len(result):04d}",
                "source":   source,
                "text":     chunk,
                "chars":    len(chunk),
            }
            if professor:
                entry["professor"] = professor
            if course:
                entry["course"] = course
            result.append(entry)
    return result


# ── LOADERS ─────────────────────────────────────────────────────────────────

def load_academicjobs(path: str, source: str) -> list[dict]:
    with open(path, encoding="utf-8", errors="ignore") as f:
        raw = f.read()
    records = extract_academicjobs(raw)
    all_chunks = []
    for rec in records:
        all_chunks.extend(chunk_text(rec["text"], source, professor=rec["professor"]))
    return all_chunks


def load_rmp(path: str, source: str) -> list[dict]:
    with open(path, encoding="utf-8", errors="ignore") as f:
        raw = f.read()
    records = extract_rmp_reviews(raw)
    all_chunks = []
    for rec in records:
        all_chunks.extend(chunk_text(rec["text"], source,
                                     professor=rec.get("professor"),
                                     course=rec.get("course")))
    return all_chunks


def load_coursicle(path: str, source: str) -> list[dict]:
    with open(path, encoding="utf-8", errors="ignore") as f:
        raw = f.read()
    records = extract_coursicle_reviews(raw)
    all_chunks = []
    for rec in records:
        all_chunks.extend(chunk_text(rec["text"], source,
                                     professor=rec.get("professor"),
                                     course=rec.get("course")))
    return all_chunks


def load_generic(path: str, source: str) -> list[dict]:
    with open(path, encoding="utf-8", errors="ignore") as f:
        raw = f.read()
    return chunk_text(generic_clean(raw), source)


SPECIAL_LOADERS = {
    "AcademiaSc.txt":  load_academicjobs,
    "RateMySC.txt":    load_rmp,
    "CoursicleSC.txt": load_coursicle,
}


# ── MAIN ────────────────────────────────────────────────────────────────────

def main():
    all_chunks = []
    print(f"\n{'Source':<25} {'Chunks':>6}  {'Avg':>5}  {'w/prof':>7}")
    print("─" * 48)

    for filename, source_name in FILES.items():
        filepath = os.path.join(INPUT_DIR, filename)
        if not os.path.exists(filepath):
            print(f"  [SKIP] {filename}")
            continue
        loader = SPECIAL_LOADERS.get(filename, load_generic)
        chunks = loader(filepath, source_name)
        all_chunks.extend(chunks)
        avg = sum(c["chars"] for c in chunks) / len(chunks) if chunks else 0
        with_prof = sum(1 for c in chunks if c.get("professor"))
        print(f"  {source_name:<23} {len(chunks):>6}  {avg:>5.0f}c  {with_prof:>7}")

    # Save outputs
    json_path = os.path.join(OUTPUT_DIR, "chunks.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)

    txt_path = os.path.join(OUTPUT_DIR, "chunks_readable.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        for c in all_chunks:
            meta = f"[{c['chunk_id']}]"
            if c.get("professor"):
                meta += f"  prof={c['professor']}"
            if c.get("course"):
                meta += f"  course={c['course']}"
            meta += f"  ({c['chars']} chars)"
            f.write(meta + "\n")
            f.write(c["text"] + "\n")
            f.write("-" * 60 + "\n")

    over = [c for c in all_chunks if c["chars"] > MAX_CHARS]
    print("─" * 48)
    print(f"  Total chunks        : {len(all_chunks)}")
    print(f"  Over {MAX_CHARS} chars      : {len(over)}  ← should be 0")
    print(f"  With professor name : {sum(1 for c in all_chunks if c.get('professor'))}")
    print(f"  With course code    : {sum(1 for c in all_chunks if c.get('course'))}")
    print(f"\n  chunks.json         → Milestone 4 embedder")
    print(f"  chunks_readable.txt → human inspection")


if __name__ == "__main__":
    main()
