import os
import re
import json

# ── CONFIG ──────────────────────────────────────────────────────────────────
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

INPUT_DIR  = "."
OUTPUT_DIR = "."
MIN_CHARS  = 80
MAX_CHARS  = 300

# ── NOISE PATTERNS ───────────────────────────────────────────────────────────
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
    r"^\d{1,2}/\d{1,2}/\d{4}$",
    r"^\d+ – invalid date$",
    r"^(to be announced|view all conferences →).*",
    # CourseBook specific — semester code lists and nav
    r"^\(\d{2}[suf]\)\s*\d{4}.*",
    r"^(syllabus policies|syllabus templates|class search|guided search|my classes|my events|instruction modalit).*",
    r"^(20\d{2} (fall|spring|summer))(\s+\(\d{2}[suf]\))?$",
    # Niche specific
    r"^(we use cookies|ok$|skip to main content|find a college|the following text input).*",
    r"^(log in|sign up|college search|college rankings|grad school|scholarships|admissions calculator|write a review).*",
    r"^(overview|academics|majors|cost|admissions|campus life|students|after college|rankings|reviews)$",
    r"^(explore academics at similar colleges|how are the academics|what students say).*",
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


# ── QUALITY FILTER ───────────────────────────────────────────────────────────
# Only keep chunks that read like student opinions or professor information.
# Drop sources that are purely structural/admin with no review content.

REVIEW_SIGNALS = [
    "professor", "prof ", "class", "course", "exam", "grade", "lecture",
    "homework", "attendance", "syllabus", "easy", "hard", "difficult",
    "recommend", "taught", "teacher", "student", "test", "assignment",
    "grading", "textbook", "midterm", "final", "project", "quiz",
    "boring", "engaging", "helpful", "approachable", "curved", "office hours",
    "take again", "dr.", "department", "research", "phd",
    "university of texas at dallas", "utd", "review", "rating",
    # UTDgrades synthesized sentence terms
    "rmp score", "level of difficulty", "would take", "tagged this class",
    "teaches", "tough grader", "lecture heavy", "caring", "respected",
    "pop quizzes", "extra credit", "group projects", "participation",
]

# These sources scraped only nav/structural pages — nothing reviewable
SKIP_SOURCES = {"UTD UES", "Uloop"}


def is_review_chunk(chunk: dict) -> bool:
    if chunk["source"] in SKIP_SOURCES:
        return False
    text = chunk["text"].lower()
    return any(sig in text for sig in REVIEW_SIGNALS)


# ── ACADEMICJOBS EXTRACTOR ───────────────────────────────────────────────────
def extract_academicjobs(raw: str) -> list[dict]:
    records = []
    sections = re.split(r"Rate My Professor\s+([A-Z][^\n]+)\n", raw)
    i = 1
    while i < len(sections) - 1:
        professor_name = sections[i].strip()
        body = sections[i + 1]
        i += 2
        about_match = re.search(
            r"About\s+\w+\s*\n(.*?)(?=RELATED JOBS|RELATED CONFERENCES|ENGINEERING JOBS|MATHEMATICS JOBS|BUSINESS|GEOSCIENCE|$)",
            body, re.DOTALL | re.IGNORECASE
        )
        if not about_match:
            continue
        about_text = about_match.group(1).strip()
        lines = about_text.splitlines()
        kept = [l.strip() for l in lines if l.strip() and not is_noise(l) and len(l.strip()) > 30]
        clean = " ".join(kept)
        if len(clean) >= MIN_CHARS:
            records.append({"professor": professor_name, "text": clean})
    return records


# ── RMP EXTRACTOR ────────────────────────────────────────────────────────────
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
            records.append({"professor": professor, "department": department,
                            "course": course, "text": line})
        i += 1
    return records


# ── COURSICLE EXTRACTOR ──────────────────────────────────────────────────────
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


# ── GENERIC CLEANER ──────────────────────────────────────────────────────────
def generic_clean(raw: str) -> str:
    lines = raw.splitlines()
    kept = [l.strip() for l in lines if not is_noise(l)]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(kept)).strip()


# ── CHUNKER ──────────────────────────────────────────────────────────────────
# Global counter ensures every chunk_id is unique across all sources
_CHUNK_COUNTER = {"n": 0}


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
            _CHUNK_COUNTER["n"] += 1
            entry = {
                "chunk_id": f"{source.replace(' ', '_')}_{_CHUNK_COUNTER['n']:05d}",
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


# ── LOADERS ──────────────────────────────────────────────────────────────────
def load_academicjobs(path: str, source: str) -> list[dict]:
    with open(path, encoding="utf-8", errors="ignore") as f:
        raw = f.read()
    records = extract_academicjobs(raw)
    chunks = []
    for rec in records:
        chunks.extend(chunk_text(rec["text"], source, professor=rec["professor"]))
    return chunks


def load_rmp(path: str, source: str) -> list[dict]:
    with open(path, encoding="utf-8", errors="ignore") as f:
        raw = f.read()
    records = extract_rmp_reviews(raw)
    chunks = []
    for rec in records:
        chunks.extend(chunk_text(rec["text"], source,
                                 professor=rec.get("professor"),
                                 course=rec.get("course")))
    return chunks


def load_coursicle(path: str, source: str) -> list[dict]:
    with open(path, encoding="utf-8", errors="ignore") as f:
        raw = f.read()
    records = extract_coursicle_reviews(raw)
    chunks = []
    for rec in records:
        chunks.extend(chunk_text(rec["text"], source,
                                 professor=rec.get("professor"),
                                 course=rec.get("course")))
    return chunks


def load_generic(path: str, source: str) -> list[dict]:
    with open(path, encoding="utf-8", errors="ignore") as f:
        raw = f.read()
    return chunk_text(generic_clean(raw), source)


# ── UTDGRADES EXTRACTOR ──────────────────────────────────────────────────────
# Each professor block contains: course code, professor name, semester,
# RMP score, difficulty, would-take-again %, and tags.
# We synthesize these into a readable sentence so it embeds like natural text.

def extract_utdgrades(raw: str) -> list[dict]:
    records = []
    lines = [l.strip() for l in raw.splitlines()]

    i = 0
    while i < len(lines):
        # Detect a professor block header: "CS 1134.101" style
        course_section = re.match(r"^([A-Z]{2,4}\s+\d{4})\.\S+$", lines[i])
        if not course_section:
            i += 1
            continue

        course_code = course_section.group(1)

        # Next line should be "LastName, FirstName - Semester Year"
        if i + 1 >= len(lines):
            i += 1
            continue
        prof_sem = re.match(r"^(.+?)\s*-\s*((?:Fall|Spring|Summer)\s+\d{4})$",
                            lines[i+1])
        if not prof_sem:
            i += 1
            continue

        prof_raw  = prof_sem.group(1).strip()   # e.g. "Karrah, Shyam S"
        semester  = prof_sem.group(2).strip()

        # Reformat name: "Last, First" → "First Last"
        name_parts = prof_raw.split(",", 1)
        if len(name_parts) == 2:
            professor = f"{name_parts[1].strip()} {name_parts[0].strip()}"
        else:
            professor = prof_raw

        # Scan ahead for rating fields (within next 30 lines)
        rmp_score  = None
        difficulty = None
        would_take = None
        tags       = []

        j = i + 2
        end = min(i + 35, len(lines))
        collecting_tags = False

        while j < end:
            ln = lines[j]
            # Course rating like "4.65/5"
            if re.match(r"^\d\.\d+/5$", ln):
                j += 1
                continue

            def next_val(idx):
                """Return the next non-empty line after idx."""
                k = idx + 1
                while k < end and not lines[k]:
                    k += 1
                return lines[k] if k < end else ""

            if ln == "RMP Score":
                v = next_val(j)
                if re.match(r"^\d+\.?\d*$", v):
                    rmp_score = v
                j += 1
                continue
            if ln == "Level of difficulty":
                v = next_val(j)
                if re.match(r"^\d+\.?\d*$", v):
                    difficulty = v
                j += 1
                continue
            if ln == "Would take again":
                v = next_val(j)
                if re.match(r"^\d+%$", v):
                    would_take = v
                j += 1
                continue
            if ln == "Tags":
                collecting_tags = True
                j += 1
                continue
            if collecting_tags:
                # Tags end when we hit "UTD Grades" or a new course header
                if ln in ("UTD Grades", "UTD") or re.match(r"^[A-Z]{2,4}\s+\d{4}", ln):
                    break
                if ln and not re.match(r"^\d+$", ln) and ln not in ("GRADES",):
                    tags.append(ln)
            j += 1

        # Build a natural-language summary sentence
        parts = []
        parts.append(f"{professor} taught {course_code} in {semester}.")
        if rmp_score:
            parts.append(f"RMP score: {rmp_score}/5.")
        if difficulty:
            parts.append(f"Difficulty: {difficulty}/5.")
        if would_take:
            parts.append(f"{would_take} of students would take them again.")
        if tags:
            parts.append(f"Students tagged this class as: {', '.join(tags)}.")

        text = " ".join(parts)
        if len(text) >= 80:
            records.append({
                "professor": professor,
                "course":    course_code,
                "text":      text,
            })

        i += 1

    return records


def load_utdgrades(path: str, source: str) -> list[dict]:
    with open(path, encoding="utf-8", errors="ignore") as f:
        raw = f.read()
    records = extract_utdgrades(raw)
    chunks = []
    for rec in records:
        chunks.extend(chunk_text(rec["text"], source,
                                 professor=rec["professor"],
                                 course=rec["course"]))
    return chunks


# ── COURSEBOOK EXTRACTOR ─────────────────────────────────────────────────────
# CourseBook has no evaluation scores or student comments — only course
# listings with instructor names and course descriptions.
# We extract: course title, course code, instructor, and description (if any).

def extract_coursebook(raw: str) -> list[dict]:
    records = []
    lines = [l.strip() for l in raw.splitlines()]
    n = len(lines)

    i = 0
    while i < n:
        # Match listing header: "ACCT 2301.001"
        sec = re.match(r"^([A-Z]{2,6})\s+(\d{4})\.\d{3}[A-Z0-9]*$", lines[i])
        if not sec:
            i += 1
            continue

        course_code = f"{sec.group(1)} {sec.group(2)}"

        if i + 2 >= n:
            i += 1
            continue

        title_raw  = lines[i+1]
        instructor = lines[i+2]

        # Skip if next line looks like a schedule, not a name
        if re.match(r"^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|\d)", instructor):
            i += 1
            continue
        if not instructor or is_noise(instructor) or len(instructor) < 3:
            i += 1
            continue

        # Clean title
        title_clean = re.sub(r"\s*\(\d+ Semester Credit Hours?\)", "", title_raw).strip()
        if not title_clean:
            i += 1
            continue

        # Look ahead for Description: and Instructor(s): in the detail block
        # (appears within ~60 lines of the section header)
        description = None
        detail_instructor = None
        j = i + 3
        end = min(i + 70, n)
        while j < end:
            ln = lines[j]
            if ln == "Description:":
                # Grab the full description line (it's on the next non-empty line,
                # and may be one long line or span a few lines)
                desc_parts = []
                k = j + 1
                while k < min(j + 8, n):
                    lk = lines[k]
                    if lk in ("Enrollment Reqs:", "Instructor(s):", "Schedule:",
                               "Syllabus:", "Evaluation:", "College:", "TA/RA(s):"):
                        break
                    if lk and not is_noise(lk) and len(lk) > 10:
                        desc_parts.append(lk)
                    k += 1
                if desc_parts:
                    description = " ".join(desc_parts)
                    # Strip the leading "COURSE XXXX - Title (N semester credit hours)" prefix
                    description = re.sub(
                        r"^[A-Z]{2,6}\s+\d{4}\s+-\s+[^(]+\(\d+ semester credit hours?\)\s*",
                        "", description, flags=re.IGNORECASE).strip()
            elif ln == "Instructor(s):":
                if j + 1 < n:
                    detail_instructor = lines[j+1].split("・")[0].strip()
            # Stop once we hit the next section header
            elif re.match(r"^[A-Z]{2,6}\s+\d{4}\.\d{3}[A-Z0-9]*$", ln) and j > i + 5:
                break
            j += 1

        # Prefer the detail-block instructor (has email stripped cleanly)
        final_instructor = detail_instructor or instructor

        parts = [f"{final_instructor} teaches {course_code}: {title_clean}."]
        if description and len(description) > 20:
            parts.append(description)
        text = " ".join(parts)

        if len(text) >= 80:
            records.append({
                "professor": final_instructor,
                "course":    course_code,
                "text":      text,
            })

        i += 1

    return records


def load_coursebook(path: str, source: str) -> list[dict]:
    with open(path, encoding="utf-8", errors="ignore") as f:
        raw = f.read()
    records = extract_coursebook(raw)
    # Deduplicate — same professor teaching same course appears once per section
    seen = set()
    chunks = []
    for rec in records:
        key = (rec["professor"], rec["course"])
        if key in seen:
            continue
        seen.add(key)
        chunks.extend(chunk_text(rec["text"], source,
                                 professor=rec["professor"],
                                 course=rec["course"]))
    return chunks


SPECIAL_LOADERS = {
    "AcademiaSc.txt":    load_academicjobs,
    "RateMySC.txt":      load_rmp,
    "CoursicleSC.txt":   load_coursicle,
    "UTDgradeSc.txt":    load_utdgrades,
    "CourseBookSc.txt":  load_coursebook,
}


# ── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    all_chunks = []
    print(f"\n{'Source':<25} {'Raw':>5}  {'Kept':>5}  {'w/prof':>7}")
    print("─" * 50)

    for filename, source_name in FILES.items():
        filepath = os.path.join(INPUT_DIR, filename)
        if not os.path.exists(filepath):
            print(f"  [SKIP] {filename}")
            continue
        loader = SPECIAL_LOADERS.get(filename, load_generic)
        raw_chunks = loader(filepath, source_name)
        good_chunks = [c for c in raw_chunks if is_review_chunk(c)]
        all_chunks.extend(good_chunks)
        with_prof = sum(1 for c in good_chunks if c.get("professor"))
        print(f"  {source_name:<23} {len(raw_chunks):>5}  {len(good_chunks):>5}  {with_prof:>7}")

    # Verify no duplicate IDs
    ids = [c["chunk_id"] for c in all_chunks]
    dupes = len(ids) - len(set(ids))

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

    print("─" * 50)
    print(f"  Total kept          : {len(all_chunks)}")
    print(f"  Duplicate IDs       : {dupes}  ← must be 0")
    print(f"  With professor name : {sum(1 for c in all_chunks if c.get('professor'))}")
    print(f"  With course code    : {sum(1 for c in all_chunks if c.get('course'))}")
    print(f"\n  chunks.json         → run embed_and_store.py next")
    print(f"  chunks_readable.txt → human inspection")


if __name__ == "__main__":
    main()