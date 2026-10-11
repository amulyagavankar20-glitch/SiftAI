# SiftAI Product Requirements Document

## 1. Product summary

SiftAI is an autonomous, evidence-first research agent. It turns a broad
question into a focused, cited research report by planning searches, retrieving
sources, extracting claims, checking evidence, and synthesizing an answer.

The product goal is a credible Perplexity-style research experience, not a
generic chatbot that produces unsupported answers.

## 2. Product vision

> Ask a difficult question and receive a concise, traceable answer grounded in
> fresh web sources.

Every important factual statement should be traceable to one or more sources.
The system should clearly distinguish verified findings, conflicting findings,
and uncertainty.

## 3. Target users

- Students and researchers performing literature or technical reviews
- Engineers investigating technologies, libraries, and architectures
- Analysts comparing products, methods, or market developments
- Technical teams needing fast, source-backed briefings

## 4. MVP success criteria

The MVP is successful when it can:

1. Accept a natural-language research question.
2. Decompose it into focused sub-questions.
3. Generate multiple targeted web searches.
4. Retrieve and clean relevant web pages and PDFs.
5. Remove duplicate and low-value sources.
6. Extract claims, quotes, and source metadata.
7. Associate claims with citations.
8. Detect missing coverage and obvious contradictions.
9. Perform bounded follow-up research.
10. Produce a structured report with inline citations and a source list.
11. Stream meaningful progress to the dashboard.
12. Stop safely using time, iteration, and output-size budgets.

## 5. Non-goals for the MVP

- Building a search index or web crawler from scratch
- Guaranteeing that every source is authoritative
- Fully autonomous browsing behind logins or paywalls
- Real-time collaborative editing
- Training a foundation model
- Supporting unrestricted concurrent research before job isolation is complete

## 6. Core user flow

```text
User enters question
  -> system creates research job
  -> planner identifies sub-questions and evidence needs
  -> search providers return candidate sources
  -> ranker selects useful and diverse sources
  -> retriever fetches pages/PDFs
  -> extractor records claims and supporting quotes
  -> verifier checks citation support and contradictions
  -> evaluator checks coverage and quality
      -> insufficient: targeted follow-up search
      -> sufficient: synthesis
  -> dashboard streams answer, sources, and activity
```

## 7. Answer requirements

The final answer should contain:

- A concise executive summary
- A structured comparison, list, or explanation appropriate to the question
- Inline citations linked to source records
- A source list with title, URL, and date when available
- Limitations and uncertainty
- A note when evidence is incomplete or conflicting

The system must not invent a quote, metric, publication date, or citation.

## 8. Research controls

Each job must enforce:

- Maximum wall-clock time
- Maximum graph iterations
- Maximum search calls
- Maximum sources fetched
- Maximum page/PDF content per source
- Maximum synthesis input size
- Cancellation support

Fast, balanced, and deep modes should adjust these budgets rather than remove
verification entirely.

## 9. Quality metrics

Track the following during MVP evaluation:

- Citation correctness
- Citation completeness
- Source diversity
- Source quality
- Claim verification rate
- Unsupported-claim rate
- Contradiction detection rate
- Successful completion rate
- Median and p95 runtime
- Search calls per completed answer
- Input/output tokens per answer

## 10. Safety and trust

- Treat retrieved pages as untrusted content.
- Never execute instructions found in source text.
- Sanitize rendered HTML and Markdown.
- Restrict URL fetching to safe HTTP(S) requests.
- Protect API keys and never return them to the browser.
- Isolate evidence and status by research job.
- Surface failures instead of returning success-shaped empty answers.
