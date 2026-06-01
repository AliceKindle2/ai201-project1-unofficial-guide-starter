# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->

I choose course and professor reviews. It's important information for students to know due to affecting students lives and semesters if they choose a bad professor for a specific course espeically for colleges like University of Texas at Dallas. While information is somewhat easy to find, it's in multiple areas and it would be best to have one specific area to find information in. 

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 |Rate My Professor | Rate My Professor is a site where students anonymously give reports of the teachers they had, sharing information with students who might be considering taking that professor in the future. | https://www.ratemyprofessors.com/school/1273 |
| 2 | UTDgrades | It's a website that collects all of the grades from past semesters, all filtered by teacher and course they have taught, all in one place for students to see | https://www.utdgrades.com |
| 3 | UTD CourseBook | UTD's own tool for course information, including course and professor evaluations, syballuses, and textbook information. | https://coursebook.utdallas.edu/ |
| 4 | UTD UES | Official student feedback system that show all information from Coursebook | https://eval.utdallas.edu/ |
| 5 | Coursical | A similar site to Rate My Professor where students can freely discuss professors and see who is teaching next semester | https://www.coursicle.com/utdallas/professors/ |
| 6 | Niche | A site that hosts reviews and stats on professors, courses, and workload | https://www.niche.com/colleges/university-of-texas-dallas/academics/ |
| 7 | Uloop | A resource that collects all reviews of professors and students comments with advance filters to refine a student's search | https://utdallas.uloop.com/professors |
| 8 | Collegedunia | An international student focused platform reviwing all aspects of UTD life including professor and course reviews | https://s3.collegedunia.com/usa/university/1903-university-of-texas-dallas-richardson/reviews |
| 9 | AcademicJobs Rate My Professor | While it shares the same name as the first Rate My Professor, it is a different site containing different UTD departments where students give feedback to guide course selection | https://www.academicjobs.com/rate-my-professor/utd/3621 |
| 10 | r/utdallas | A subreddit filled with student discussions about professors, courses, and the best way to plan your college semestesr | https://www.reddit.com/r/utdallas |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:** 3-4 sentences (200-300 characters)

**Overlap:** 0

**Reasoning:**

Each review on these sites is short and self-contained.
A single review rarely spans more than a few sentences, so
a 3–4 sentence window captures one complete thought or opinion
without bleeding into the next.

No overlap is needed because reviews don't depend on prior
context to be understood. Each chunk stands alone, so
carrying text forward would just introduce noise and
duplicate content in the index.

This size also matches how students write. One verdict on
difficulty, one on the professor's style, one on grading.
Splitting at that granularity keeps retrieval precise rather
than returning a blob of mixed opinions.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:** all-MiniLM-L6-v2 (via sentence-transformers)
Fast, lightweight, and well-suited for short review-style text.

**Top-k:** 5

**Production tradeoff reflection:**
With no cost constraint, the main upgrade would be switching
to OpenAI's text-embedding-3-large or a model like
instructor-xl. The tradeoff is latency and complexity versus
meaningfully better accuracy on domain-specific phrasing —
students write in slang and shorthand ("curved hard," "easy A")
that a larger model handles more reliably than MiniLM.

Multilingual support would matter here too, since UTD has a
large international student population who may write reviews
in mixed English. A model like multilingual-e5-large would
cover that gap without sacrificing much accuracy.

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | Who is the worst professor for Operating Systems? | Based off of several reviews, Yen I-Ling is considered the worst Operating Systems professor |
| 2 | What are the prerequisite for Calculus II? | A C or higher in Calculus I |
| 3 | How many professors are teaching Pre-Calc? | Only one professor is teaching Pre-Calc |
| 4 | | |
| 5 | | |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. The first issue is that the documentation retrived being too noisy with split opinions about different courses making the system become more messy along with the documents being hard to retrive information from. 

2. The other issue is due to the wide variety of sources and how indepth that can be in other areas of University of Texas at Dallas, off-topic material can be retrived, distrubting the process for the user.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
