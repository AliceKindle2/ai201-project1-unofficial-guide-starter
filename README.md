# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->

I choose course and professor reviews. It's important information for students to know due to affecting students lives and semesters if they choose a bad professor for a specific course espeically for colleges like University of Texas at Dallas. While information is somewhat easy to find, it's in multiple areas and it would be best to have one specific area to find information in. 

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

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

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:** 3-4 sentences (200-300 characters)

**Overlap:** 0

**Why these choices fit your documents:** 
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

**Final chunk count:** 532 chunks in total

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:** all-MiniLM-L6-v2 via sentence-transformers

This model runs locally, requires only needing the groq key that is in the .envi code, and is fast enough
to embed all 532 chunks. It was the right choice for a project where the corpus is small, the text is short
(80–300 chars per chunk), and the queries are simple natural-language questions about professors and courses.

**Production tradeoff reflection:**

The main upgrade would be switching to OpenAI's text-embedding-3-large or Cohere's embed-v3. The core tradeoff is
accuracy versus cost and latency. all-MiniLM-L6-v2 was trained on general web text, so it handles student slang like "curved hard" or "easy A" less reliably than a larger model trained on more diverse data. A domain-specific model would close that gap meaningfully.

Context length would matter too. all-MiniLM-L6-v2 caps at 256 tokens, which is fine for our 200–300 character chunks but would
break down if chunks were longer. text-embedding-3-large supports 8,191 tokens, giving far more flexibility if the chunking strategy changed.

Multilingual support is a real concern for UTD specifically. The
student body has a large international population and some reviews
are written in mixed English or non-English entirely. A model like
multilingual-e5-large would handle that without sacrificing much
accuracy on English text.

The local-versus-API tradeoff cuts both ways. Running locally means
no per-call cost and no latency spike from a network round trip,
which mattered here. In production with thousands of daily queries,
an API-hosted model with a usage-based cost would likely be cheaper
than hosting a large model yourself, and would come with SLA
guarantees all-MiniLM-L6-v2 running on a laptop does not.

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:** The grounding instruction I gave it is that the LLM must source it's information and must match the information found in the chunks. 

**How source attribution is surfaced in the response:** The source attribution is surfaced in the response is that after each statement it is followed with [Source #], all of the sources is found in a neat sidebar next to the answer for the user to easily see what sources information came from.

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What are the prerequisites for Calculus II? | Calculus I is the prerequistes for Calculus II | I don't have enough information for that| Partially relevant | Inaccurate |
| 2 | Who are the top teachers for CS 2305? | A general list of the best teachers based on RMP results | A general list of the best teachers based on RMP results | Relevent | Accurate |
| 3 | Is CS 2336 a hard course? | yes or give general information why it's hard | yes and it's due to this specific teacher | Releant | Partically accurate |
| 4 | Who teaches introductory financial accounting? | Gives a list for teachers that teach this course | Gives a list for teachers that teach this course | Relevant | Accurate |
| 5 | How does one sign up for EPICS? | In order to sign up for a class, register it on the course page | I don't have enough information to answer this question |Partically relevant | Inaccurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:**

How to sign up for EPICS class?

**What the system returned:**

Sorry there is not enough information from these sources and proceeds to list all of the sources. 

**Root cause (tied to a specific pipeline stage):**

The root cause in this answer is in the chunks themselves, as they don't have the answer for signing up for EPICS or any classes within them. During the scrapping process, I learned that all of the prerequiste information about all classes were held in seperate pages, meaning a lot more work to scrap each one to get the information I needed. Instead I focused my attention on professors and student reviews to get general information from them and information about classes from other sources. 

**What you would change to fix it:** 

In order to fix this answer, more information needs to be scrapped from the websites, be it scrapping more pages in general one by one or scrapping off of live links. 

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**

The chunk size and overlap helped a lot with keeping information straightforward and neat for the user to get information. It helped a lot with making the RAG system less confused and what to share. 

**One way your implementation diverged from the spec, and why:**

One way my implementation has diverged from the spec is the questions about courses given it's hard to find specific places to get information without a lot of scraping of data to find specific date. 

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:* I gave Claude my cleaned documents without html, read more, and other items that weren't neccessary to the system for it to implement a script for it to load the docuements, cleans them, and produces chunks following the system. 
- *What it produced:* Claude originally produced a document with over a thousand chunks, a lot of them having information but a lot noise as well in the system. 
- *What I changed or overrode:* I had to override Claude system for allowing too much noise in like advertisement and banners into the chosen chunks, changing it so Claude focuses on professor and course information. 

**Instance 2**

- *What I gave the AI:* I gave Calude the planning.md and pipeline diagram, along with a lot of instructions for how it would make the LLM. That included what source it should use, it should use groq for it's system, grounding prompt, and to use the Gradio skeleton structure that best fit the system. 
- *What it produced:* It produced a working LLM for the site, using all of the information that I gathered and making it look nice. 
- *What I changed or overrode:* Claude was insistent using anthronpic API key at first despite me pushing back, instead changing it to Groq due to what codepath recommended 



Video Demo Link: https://www.loom.com/share/dcf3674723b54c87ac96ddc913a7e6ee