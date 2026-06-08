# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

UCI ICS/CS professor and course experiences. More specifically student opinions on professors
like Thornton, Shindler, Wong Ma, and Klefstad across courses like ICS 33, 45C, 46, 51,
and 53.

This knowledge is valuable because it answers things that students want to know like "Does the cs professor
Shindler curve? Is cs professor Wong Ma worth the difficulty? What does Thornton's grading
actually look like going into the final?" The official course catalog gives you prerequisites
and units. But it doesn't tell you how it is like or the many opinions and suggestions that people have for those professors/courses.
Students share this knowledge on Reddit and RateMyProfessors, but it is not searchable in one place like this.

---

## Document Sources

All 10 sources are saved as .txt files in the /docs folder. Each file was manually copied
from its source because both Reddit and RateMyProfessors block automated scraping.

| # | File | Source URL | Type | Content |
|---|------|-----------|------|---------|
| 1 | reddit_ics33_thornton_curve.txt | reddit.com/r/UCI/comments/14ac2rz | Reddit thread | Thornton curve details, grade going into final, passing thresholds |
| 2 | rmp_thornton_reviews.txt | ratemyprofessors.com/professor/13200 | RMP reviews | Thornton class structure, vibes, student suggestions |
| 3 | rmp_shindler_reviews.txt | ratemyprofessors.com/professor/2512998 | RMP reviews | Shindler grade curve, difficulty, exam style |
| 4 | reddit_ics46_shindler_ics53_wongma.txt | reddit.com/r/UCI/comments/dzgshs | Reddit thread | One student's take on taking Shindler + Wong Ma together |
| 5 | rmp_wongma_reviews.txt | ratemyprofessors.com/professor/2409085 | RMP reviews | Wong Ma reviews: difficulty, what you learn, grading |
| 6 | reddit_wongma_shindler_comparison.txt | reddit.com/r/UCI/comments/13kt0jd | Reddit thread | Debate: Wong Ma hard but you learn more vs. easier alternatives |
| 7 | rmp_klefstad_reviews.txt | ratemyprofessors.com/professor/17490 | RMP reviews | Klefstad reviews: teaching quality, complaints, overall impressions |
| 8 | reddit_klefstad_weird.txt | reddit.com/r/UCI/comments/ait0f5 | Reddit thread | Klefstad negative/unusual classroom experiences |
| 9 | thornton_ics46_course_reference.txt | ics.uci.edu/~thornton/ics46/CourseReference.html | Official course page | Thornton ICS 46 structure: grading breakdown, policies, expectations |
| 10 | reddit_ics51_wongma.txt | reddit.com/r/UCI/comments/n50u8g | Reddit thread | ICS 51 with Wong Ma: workload, difficulty, student experiences |

Sources span three types: Reddit threads (personal student stories), RMP
review pages (structured individual ratings), and one official course reference page. This
variety means the system can answer both factual questions (grading breakdown from the
syllabus) and experiential questions (what students actually felt about surviving the class).

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Why recursive splitting fits these documents:**

The documents are a mix of Reddit comments (2–5 sentences each), RMP reviews (1–4
sentences each), and one longer course overview page with structured paragraphs. A fixed
character split would cut mid-sentence or merge two different students' opinions into one
chunk. Recursive splitting respects the boundaries of both the opinion of a redditor and a paragraph section in the course reference document. It keeps these context-distinct chunks intact wherever possible.

**Chunk size:** 400 characters.

**Overlap:** 75 characters.

**Why these choices fit your documents:**

**Why 400 characters:**

A RMP review or Reddit comment is 200–500 characters. A 400 character chunk
captures one complete opinion without merging unrelated viewpoints. Smaller chunks (under
150 characters) will produce fragments with no context about
which class or why those fragments match too many queries and return noise. Larger chunks
(over 800 characters) would merge multiple student opinions into one embedding, making it
impossible for retrieval to match a specific claim about grading or difficulty. This is an experimental variable.

**Why 75 characters of overlap:**

Reddit threads have replies which does not repeat some important context like the professor or class taken. A reply saying "The curve saved me" is meaningless
without the comment it answered. A 75 character overlap carries just enough of the prior
sentence into the next chunk to make the reply retrievable on its own. It is small enough
not to duplicate full opinions across chunks. This is an experimental variable.




**Final chunk count:** 455 chunks across all 10 documents. 0 empty, 0 fragments.

---

## Sample Chunks

Five real chunks from different source documents. Every chunk starts with the metadata header
`[Professor: X | Source: filename.txt]` that my chunker prepends before embedding, so the
professor and source are always in the embedded text itself.

**1. Source: reddit_ics33_thornton_curve.txt** (Professor: Thornton)
> [Professor: Thornton | Source: reddit_ics33_thornton_curve.txt] Failing ICS 33. The last
> project's grade was released and I entered all my current grades into the grade calculator and
> have a 69%. The final is in a few hours and i know i won't be able to get a high enough score.
> Does Thornton curve only the final or the final grades cuz all i need is a passing grade rn.

**2. Source: reddit_ics46_shindler_ics53_wongma.txt** (Professor: Shindler/Wong Ma)
> [Professor: Shindler/Wong Ma | Source: reddit_ics46_shindler_ics53_wongma.txt] is ics 46 with
> schindler and ics 53 with wong ma together inadvisable?

**3. Source: reddit_ics51_wongma.txt** (Professor: Wong Ma)
> [Professor: Wong Ma | Source: reddit_ics51_wongma.txt] ICS 51 w/ Wong-Ma. Should I wait another
> quarter for a different professor or just take it with her? Who is the best prof for 51 for
> those who have taken it?

**4. Source: rmp_wongma_reviews.txt** (Professor: Wong Ma)
> [Professor: Wong Ma | Source: rmp_wongma_reviews.txt] Attendance: Not Mandatory / Would Take
> Again: Yes / Grade: A- / Wong-Ma is the best ICS professor I've had yet. Her lectures are
> clear and she is on top of her game.

**5. Source: reddit_wongma_shindler_comparison.txt** (Professor: Shindler/Wong Ma)
> [Professor: Shindler/Wong Ma | Source: reddit_wongma_shindler_comparison.txt] ICS 51(Wongma)
> and ICS 45C(Shindler) in fall vs ICS 46(Thornton or Shindler) and ICS 51(Nicolau) in winter,
> Which is a better course load? / Nicolau is the easiest 51, this quarter has been a joke. So
> if you want an easy load go with him.

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:** all-MiniLM-L6-v2 via sentence-transformers. Runs entirely locally
with no API key and no rate limits, which fits the free tool stack required by this project.

**Production tradeoff reflection:**

If cost was not a constraint and this was serving real students, I would weigh a few things.
all-MiniLM-L6-v2 is small and fast, but it is trained on general English so it can miss the
meaning of short slangy student reviews. I would test text-embedding-3-large from OpenAI since
it does better on short opinion text, but that adds a per-token cost and an API dependency I do
not have right now. instructor-xl is another option because it lets you prefix the query with
the task type, which could help domain matching, but it is heavier and slower to run locally.
The biggest real gap is multilingual support, UCI has a lot of international students who might
phrase things in other languages, and MiniLM is English first, so multilingual-e5 would be
worth testing for that. Context length is not a concern here because my chunks are only 400
characters, well under any model's limit. So the real tradeoff is accuracy on short domain text
and multilingual coverage versus the cost and latency of a hosted API model.

---

## Retrieval Test Results

Three queries run through the hybrid retriever, showing the top chunks it returned with their
merged score (and the semantic / BM25 split). Score = 0.6 × semantic + 0.4 × BM25.

**Query 1: "Does Thornton curve ICS 33?"**

| Rank | Score (sem / bm25) | Source | Chunk (trimmed) |
|------|--------------------|--------|-----------------|
| 1 | 1.00 (1.00 / 1.00) | reddit_ics33_thornton_curve.txt | "Failing ICS 33… have a 69%… Does Thornton curve only the final or the final grades…" |
| 2 | 0.74 (0.88 / 0.53) | reddit_ics33_thornton_curve.txt | "i'm trying to aim for a 70 on the final but if not i hope the curve saves me…" |
| 3 | 0.53 (0.88 / 0.00) | reddit_ics33_thornton_curve.txt | "Come on man, don't give up yet… if you don't pass you can just retake the class…" |

*Why these are relevant:* all three are from the Thornton curve thread and directly discuss a
student near the pass line asking whether Thornton curves, the exact topic of the query. The top
chunk scores a perfect 1.00 on both halves because it contains both the meaning ("curve") and
the literal keywords ("Thornton", "ICS 33"), so semantic and BM25 agree.

**Query 2: "Is Wong Ma a tough professor for ICS 51?"**

| Rank | Score (sem / bm25) | Source | Chunk (trimmed) |
|------|--------------------|--------|-----------------|
| 1 | 0.87 (0.98 / 0.70) | rmp_wongma_reviews.txt | "Would Take Again: Yes… Wong-Ma is the best ICS professor I've had yet. Her lectures are clear…" |
| 2 | 0.83 (0.88 / 0.76) | rmp_wongma_reviews.txt | "Just like ICS 51, ICS 53 with Wong-Ma is a hard course. However…" |
| 3 | 0.79 (0.92 / 0.61) | rmp_wongma_reviews.txt | "This is the first ics professor who is so on top of her game…" |

*Why these are relevant:* all three are Wong Ma reviews that speak to difficulty and quality for
her ICS courses, which is what the query asks. BM25 is nonzero on every chunk here because "Wong
Ma" and "51" appear as literal keywords, so the keyword half reinforces the semantic match
instead of fighting it (the opposite of what happened in the Shindler failure case below).

**Query 3: "Is Wong Ma worth taking even though he is hard?"**

| Rank | Score (sem / bm25) | Source | Chunk topic |
|------|--------------------|--------|-------------|
| 1 | 0.82 (0.90 / 0.70) | rmp_wongma_reviews.txt | "would take again," praises lectures despite difficulty |
| 2 | 0.79 (0.93 / 0.56) | rmp_wongma_reviews.txt | hard course but you learn a lot |
| 3 | 0.60 (1.00 / 0.00) | rmp_wongma_reviews.txt | strong positive review of Wong Ma |

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**

"You are the Unofficial UCI Professor Guide. You answer questions about UCI "
    "ICS/CS professors and courses using ONLY the numbered context passages provided "
    "in the user message.\n\n"
    "STRICT RULES:\n"
    "1. Use ONLY information found in the provided context passages. Do NOT use any "
    "prior knowledge about these professors, courses, or universities.\n"
    "2. If the context does not contain enough information to answer the question, "
    f'reply with EXACTLY this sentence and nothing else: "{NO_INFO}"\n'
    "3. Do not guess, infer beyond the text, or add general advice that is not "
    "supported by the passages.\n"
    "4. When you state a fact, it must be traceable to one of the passages.\n"
    "Answer concisely in 2-5 sentences."

**How source attribution is surfaced in the response:**

Source attribution comes from the retrieved chunk's metadata, never from the model's text
answer. After the LLM responds, ask() in query.py walks the chunks that were actually retrieved
and collects each unique source filename in rank order, and returns them as a separate sources
list next to the answer. The Gradio app then shows those sources in their own "Retrieved from"
box under the answer. I did it this way on purpose so the model cannot make up or mis-cite a
source, the citations are tied to the chunks the retriever really pulled, not to whatever the
model decides to write. There is also a guard: if the model returns the exact "I don't have
enough information" sentence, the sources list is forced to empty so a refusal never shows fake
citations.

---

## Example Responses

Two real answers with source attribution visible, plus one out-of-scope query showing the
refusal. Sources are printed under each answer (in the Gradio UI they appear in the "Retrieved
from" box).

**Example 1 (works well):**

> **Q:** Is Wong Ma worth taking even though he is hard?
>
> **A:** According to the passages, despite being a hard professor, Wong Ma is worth taking.
> Multiple reviewers stated they "Would Take Again: Yes," and praised her as an "adept lecturer"
> who gives "amazing lectures" and "extra credit opportunities," even though her courses are
> considered difficult.
>
> **Sources:** rmp_wongma_reviews.txt

**Example 2 (works well):**

> **Q:** Is Wong Ma a tough professor for ICS 51?
>
> **A:** According to Passage 4, Wong-Ma's ICS 51 course is "definitely on the harder side" and
> the content is "quite difficult," and Passage 5 rates the difficulty 4.0. However it also notes
> that with hard work an A is possible, so it is challenging but manageable.
>
> **Sources:** rmp_wongma_reviews.txt

**Example 3 (out-of-scope refusal):**

> **Q:** What is the parking situation at UCI?
>
> **A:** I don't have enough information on that.
>
> **Sources:** (none)

The parking question has no supporting documents in the corpus, so retrieval returns nothing
useful and the grounding rule forces the exact refusal sentence with no sources, instead of the
model answering from general knowledge.

---

## Query Interface

The interface is a Gradio web app (app.py) served at http://localhost:7860.

**Input field:** a single text box, "Your question," where the user types a natural-language
question about a UCI ICS/CS professor or course. Pressing Enter or the "Ask" button submits it.

**Output fields:** two read-only text boxes:
- **Answer** — the grounded answer generated from the retrieved chunks (or the refusal sentence).
- **Retrieved from** — the list of source filenames the answer is based on, one per line, taken
  from the retrieved chunks' metadata (not parsed from the answer text).

**Sample interaction transcript:**

```
Your question:  Is Wong Ma a tough professor for ICS 51?

Answer:         According to Passage 4, Wong-Ma's ICS 51 course is "definitely on the
                harder side" and the content is "quite difficult" (difficulty 4.0).
                However, with hard work it is possible to get an A, so it is challenging
                but manageable.

Retrieved from: • rmp_wongma_reviews.txt
```

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | Does Thornton curve ICS 33? | Yes — a low score going into the final can still pass due to a curve; specific grade ranges appear in the Reddit thread. | Says Thornton curves (cites a student curved 13%) but hedges that it is not explicitly tied to ICS 33, and notes the course-reference page says grading is "neither a normal curve nor a straight scale." | Relevant | Partially accurate |
| 2 | Is Wong Ma worth taking even though he is hard? | Mixed — many say yes (you learn deeply), others recommend easier alternatives if GPA is the priority. | Says yes, worth taking: reviewers "would take again," praise lectures and extra credit despite difficulty. Only surfaces the positive side. | Relevant | Accurate |
| 3 | What is Shindler's grading structure like in ICS 46? | Exam-heavy with a curve; practicing his problem sets is key to passing. | "I don't have enough information on that." ie declined to answer. | Partially relevant | Inaccurate |
| 4 | Is Wong Ma a tough professor for ICS 51? | Yes, one of the harder ICS profs; heavy workload, hard exams, but the difficulty pays off. | Yes — ICS 51 is "on the harder side" and "quite difficult" (difficulty 4.0), but manageable with effort / an A is possible. | Relevant | Accurate |
| 5 | Is taking ICS 51 (Wong Ma) + ICS 45C (Shindler) in fall a good idea vs. ICS 46 + ICS 51 (Nicolau) in winter? | Mixed — Wong Ma + Shindler together is a very heavy load; some suggest splitting across quarters; no clear consensus. | Compares each: Wong Ma 51 hard, Shindler 45C "learn a lot but rip your grade," Nicolau 51 "a joke," Shindler 46 "relatively easy"; concludes the fall pairing is more challenging. | Relevant | Partially accurate |

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


What is Shindler's grading structure like in ICS 46?

**What the system returned:**

"I don't have enough information on that." ie declined to answer.

**Root cause (tied to a specific pipeline stage):**

This is a retrieval failure, the ICS 46 Shindler content is actually in my corpus (reviews
tagged ICS46, and a Reddit chunk saying ICS 46 with Shindler is "relatively easy" with "midterms
around 4-6 questions") but retrieval never grabbed those chunks. Two things upstream cause it.
First, chunking split the RMP reviews into tiny tag-only fragments like "Clear grading criteria"
and "Test heavy", and the query "grading structure" embeds almost identically to those keyword
tags, so they win on semantic score and crowd out the richer ICS 46 chunks. Second, BM25 should
have pinned retrieval to the course with the "46" keyword, but my tokenizer is a bare
.lower().split() with no punctuation handling, so the query token is "46?" (with the question
mark) while the reviews write "ICS46" glued together, the two never match and BM25 scores 0.00
on everything. The model then got 5 content-free tag chunks and correctly refused, so the
refusal was honest but the real failure is that retrieval handed it junk instead of the ICS 46
reviews that were right there.

**What you would change to fix it:**

I would fix this at the chunking and tokenization stage, not the prompt, since the ICS 46 reviews
are already in the corpus. First, I would strip punctuation in the BM25 tokenizer and split glued
course tokens so "46?", "ICS46" and "ics 46" all normalize to the same "46" token, that alone
would let the keyword half of my hybrid search actually pin retrieval to the right course.
Second, I would keep each full RMP review's prose together with its tags instead of letting the
bullet tags ("Test heavy", "Clear grading criteria") get split into tiny standalone fragments,
so those keyword-only chunks stop out-ranking the richer reviews that actually describe the
class. The refusal was the honest response given the junk chunks it
received, the fix is getting retrieval to hand it the good chunks instead.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**

Thinking about the decisions before starting to code and justify them made the development process easier as I only had to experiment  with variables like chunking size, scoring function for retrieval instead of the more fundamental decisions. This early cost made development smoother and more effective.

**One way your implementation diverged from the spec, and why:**

My architecture diagram showed the chunking stage using LangChain's RecursiveCharacterTextSplitter,
but I wrote the recursive splitter in pure Python instead since I did not want a whole LangChain
dependency just to split text on a list of separators. The behavior is the same as the diagram
intended (same separators, chunk size, and overlap), it is just my own code instead of a library.

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1 — the chunking function**

- *What I gave the AI:* My Chunking Strategy and Documents sections from planning.md, and I
  asked it to implement chunk_documents() with chunk_size 400 and overlap 75 and the metadata
  header prepended to each chunk.
- *What it produced:* A version that used LangChain's RecursiveCharacterTextSplitter to do the
  splitting.
- *What I changed or overrode:* I had it rewrite the splitter in pure Python instead, because I
  did not want a whole LangChain dependency for one function and my AI Tool Plan had already
  described it as pure-Python. The result is the _recursive_split() in chunk.py that tries the
  separators in order itself, and the comment there literally notes it "replaces LangChain
  dependency."

**Instance 2**

- *What I gave the AI:* The grounding requirement (answer only from retrieved context, refuse if
  not enough info) and the Gradio skeleton, and asked for a function that returns the answer plus
  its sources.
- *What it produced:* A first version that pulled the source names out of the model's text
  answer, basically parsing whatever the LLM wrote to figure out which sources to list.
- *What I changed or overrode:* I changed it so the sources come programmatically from the
  retrieved chunks' metadata instead of from the model's text. That way the model physically
  cannot make up or mis-cite a source, the citations always match the chunks the retriever
  actually pulled. I also added the guard that empties the sources list when the model returns
  the "I don't have enough information" refusal, so a refusal never shows citations.
