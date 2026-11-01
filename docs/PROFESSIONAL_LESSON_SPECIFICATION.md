# CCAR-P Intelligence Academy 2.0 --- Professional Lesson Specification

**Release:** 2.0 learning-standard upgrade\
**Depth:** Professional architect\
**Delivery:** Detailed written lessons + diagrams + code + practical
laboratories\
**Operating model:** Local-first; no mandatory paid API, model
subscription, or external inference endpoint

## 1. Product purpose

The Academy is an independent professional learning environment for
developing the judgement and practical skills needed to design,
implement, evaluate, secure, operate, and communicate Claude-powered
systems.

It is not an Anthropic product, an official exam simulator, or a source
of official examination questions. The curriculum must be checked
against the current public certification objectives and current
Anthropic documentation before each study cycle.

## 2. Learning outcomes

By completing a professional lesson, the learner should be able to:

1.  Explain the concept from first principles and distinguish it from
    adjacent concepts.
2.  Identify the problem, constraints, and requirements that make the
    concept relevant.
3.  Select and justify an appropriate architecture or implementation
    pattern.
4.  Implement or inspect a representative solution.
5.  Evaluate quality, failure modes, security, cost, latency, and
    operational implications.
6.  Communicate the decision to technical and non-technical
    stakeholders.
7.  Transfer the learning to a new scenario rather than merely recall a
    definition.

## 3. Required lesson anatomy

Every full professional lesson must contain the following sections. A
lesson may mark a section as not applicable, but must explain why.

  ---------------------------------------------------------------------
  Section                            Required content
  ---------------------------------- ----------------------------------
  Learning outcomes                  3--6 observable outcomes using
                                     action verbs

  Prerequisites                      Concepts, tools, and assumed
                                     knowledge

  Executive orientation              Why the topic matters in real
                                     systems

  First-principles explanation       Definitions, mechanisms,
                                     boundaries, and mental model

  Technical deep dive                Components, data/control flow,
                                     interfaces, constraints, and
                                     relevant algorithms

  Architecture pattern               When to use it, when not to,
                                     alternatives, and decision
                                     criteria

  Diagram                            Mermaid flowchart/sequence diagram
                                     or a clearly described
                                     architecture diagram

  Worked example                     A realistic end-to-end scenario
                                     with assumptions

  Implementation lab                 Step-by-step exercise, code or
                                     pseudocode, expected output, and
                                     verification

  Trade-off analysis                 Quality, latency, cost,
                                     complexity, reliability,
                                     maintainability, and portability

  Failure modes                      At least 4 failure cases,
                                     symptoms, causes, mitigations, and
                                     recovery

  Security and governance            Trust boundaries, permissions,
                                     data handling, abuse cases,
                                     auditability

  Evaluation                         Metrics, test design, acceptance
                                     criteria, and regression strategy

  Production checklist               Readiness checks before deployment

  Case study                         A realistic scenario requiring an
                                     architectural decision

  Knowledge check                    5--10 questions including
                                     explanation, application, and
                                     judgement

  Architect challenge                An open-ended design task with
                                     rubric and exemplar reasoning

  Further reading                    Primary documentation first, then
                                     high-quality supporting references

  Key takeaways                      Concise synthesis and links to
                                     related lessons
  ---------------------------------------------------------------------

## 4. Technical accuracy and source policy

-   Prefer current primary documentation from Anthropic for
    Claude-specific behaviour, API features, tool use, prompt caching,
    model capabilities, and platform limits.
-   Label version-sensitive details with an `as_of` date and source
    URLs.
-   Never fabricate API parameters, model names, limits, certification
    objectives, or official exam questions.
-   Clearly distinguish a general AI engineering principle from a
    Claude-specific implementation detail.
-   Code must be labelled as runnable, illustrative, or pseudocode.
    Include dependencies and execution assumptions.
-   If a capability depends on a hosted Claude API, explain it without
    requiring the learner to call a paid endpoint.
-   Do not imply that local deterministic examples reproduce hosted
    Claude model behaviour.

## 5. Seven-domain curriculum architecture

The current seven-domain structure is retained as the organising
taxonomy:

### D1 --- Solution Design & Architecture

System decomposition; requirements and constraints; deterministic
workflows vs agentic systems; single-agent and multi-agent patterns;
orchestration; state; human-in-the-loop; reliability; architecture
decision records.

### D2 --- Claude Models, Prompting & Context Engineering

Model selection; system instructions; prompt design; context windows and
token budgeting; context assembly; retrieval and memory; prompt caching;
structured outputs; long-context strategies; model limitations.

### D3 --- Integration & Tool Use

Claude API integration concepts; tool schemas; tool calling loops; MCP
concepts and integrations; authentication and authorization; retries and
idempotency; external systems; event-driven patterns; sandboxing.

### D4 --- Evaluation, Testing & Optimisation

Evaluation design; test sets; task success; rubric-based evaluation;
model grading and human review; regression tests; adversarial testing;
latency and cost measurement; observability; iterative optimisation.

### D5 --- Governance, Safety & Risk Management

Threat modelling; prompt injection; data leakage; least privilege; tool
safety; privacy; retention; audit trails; policy enforcement; human
oversight; incident response; deployment risk.

### D6 --- Stakeholder Communication & Lifecycle Management

Discovery; requirements traceability; architecture communication;
decision records; stakeholder alignment; change management; release
lifecycle; service ownership; documentation; incident communication.

### D7 --- Developer Productivity & Operational Enablement

Developer workflows; reusable components; testing harnesses; CI/CD
concepts; environment configuration; version control; deployment
patterns; monitoring; runbooks; team enablement and technical standards.

These are curriculum categories, not a claim that they reproduce the
exact official exam blueprint. Map lessons to verified current
objectives when the official blueprint is available.

## 6. Mastery model

Track four dimensions independently:

-   **Knowledge:** Can explain the principle accurately.
-   **Application:** Can implement or adapt the pattern.
-   **Judgement:** Can compare alternatives and defend a choice.
-   **Operational readiness:** Can anticipate, detect, and recover from
    failures.

Suggested mastery progression:

1.  Unseen --- no evidence yet.
2.  Understand --- can explain with prompts or notes.
3.  Apply --- completes a guided exercise.
4.  Analyse --- compares patterns and diagnoses failure.
5.  Architect --- independently designs and defends a solution.
6.  Transfer --- succeeds in a novel scenario.

Do not mark a learner as architect-level based on confidence alone.
Require evidence from a lab, case study, or assessment.

## 7. Assessment design

Use original practice material, not leaked or purported official exam
items.

A balanced lesson assessment should include: - 2 recall/comprehension
checks - 2 applied technical questions - 2 scenario-based architecture
decisions - 1 failure-analysis question - 1 stakeholder explanation or
design defence

Each question should have: - stable ID, domain, lesson ID, difficulty,
question type - prompt and optional options - correct answer or scoring
rubric - explanation of why the answer is defensible - explanation of
plausible distractors where relevant - source/provenance and
last-reviewed date

Scoring should reward reasoning and trade-off awareness, not only
keyword matching. Open-ended responses should be self-assessed against a
visible rubric unless a human reviewer or optional model integration is
available.

## 8. Zero-paid-API architecture

The base release must work without any model API key: - Markdown/JSON
lesson content stored locally. - Streamlit renders lessons and Mermaid
diagrams as text or supported diagrams. - SQLite stores progress,
attempts, notes, and assessment evidence. - Deterministic quiz scoring
for objective questions. - Rubric-based self-assessment for open-ended
tasks. - Browser/device text-to-speech where available. - JSON/CSV
import and export for content expansion and backups.

Optional future integrations must be disabled by default and clearly
labelled. Never silently send learner notes or assessment answers to an
external service.

## 9. Lesson content quality gates

A lesson is not "professional" until it passes these checks:

-   [ ] Outcomes are observable and testable.
-   [ ] First-principles explanation is technically sound.
-   [ ] At least one diagram or architecture flow is included.
-   [ ] Worked example contains assumptions and constraints.
-   [ ] Implementation lab has verification steps.
-   [ ] Trade-offs compare at least two viable options.
-   [ ] Four or more failure modes include mitigations.
-   [ ] Security and governance are addressed.
-   [ ] Evaluation metrics and acceptance criteria are explicit.
-   [ ] Case study requires a decision, not simple recall.
-   [ ] Assessment includes answers/rubrics and explanations.
-   [ ] Sources and version-sensitive claims are dated.

## 10. Recommended lesson build order

For a short preparation window, prioritise: 1. Agentic vs deterministic
architecture and orchestration. 2. Context engineering and prompt
architecture. 3. Tool use, tool loops, and MCP. 4. Evaluation and
reliability engineering. 5. Security, prompt injection, and least
privilege. 6. Production deployment, observability, and lifecycle. 7.
Architecture communication and decision defence.

## 11. Full professional curriculum inventory

This release includes 29 professional lessons across the seven learning
domains. The mapping is an independent study taxonomy, not a claim that
it reproduces the official Anthropic examination blueprint.

### D1 --- Solution Design & Architecture (6 lessons)

-   D1-L01 Requirements Decomposition and AI Solution Architecture
-   D1-L02 Agentic Workflows, Orchestration and Control
-   D1-L03 Choosing Deterministic Workflows Versus Agentic Systems
-   D1-L04 Architecture Trade-off Analysis and Decision Records
-   D1-L05 Human-in-the-Loop Design and Approval Gates
-   D1-L06 Reliability Engineering and Graceful Degradation

### D2 --- Claude Models, Prompting & Context Engineering (4 lessons)

-   D2-L01 Context Engineering for Production Claude Systems
-   D2-L02 Prompt Architecture and Instruction Hierarchy
-   D2-L03 Model Selection, Structured Outputs and Response Contracts
-   D2-L04 Prompt Chaining and Multi-Step Reasoning Workflows

### D3 --- Integration & Tool Use (4 lessons)

-   D3-L01 Tool Use Architecture and Safe Execution
-   D3-L02 Model Context Protocol and Integration Boundaries
-   D3-L03 API Integration, Error Handling and Idempotent Operations
-   D3-L04 Retrieval-Augmented Generation Architecture

### D4 --- Evaluation, Testing & Optimisation (5 lessons)

-   D4-L01 Evaluation Frameworks for LLM and Agentic Systems
-   D4-L02 Reliability, Observability and Performance Optimisation
-   D4-L03 LLM-as-Judge Evaluation and Human Calibration
-   D4-L04 Regression Testing and Release Gates for AI Behaviour
-   D4-L05 Performance Optimisation, Caching and Cost Engineering

### D5 --- Governance, Safety & Risk Management (3 lessons)

-   D5-L01 Threat Modelling and Prompt Injection Defence
-   D5-L02 Privacy, Governance and Human Oversight
-   D5-L03 Secure Tool Permissions and Capability-Based Access

### D6 --- Stakeholder Communication & Lifecycle Management (4 lessons)

-   D6-L01 Stakeholder Discovery and Architecture Decision Records
-   D6-L02 AI System Lifecycle, Change Management and Service Ownership
-   D6-L03 Technical Communication for Architecture Reviews
-   D6-L04 Requirements Traceability and Stakeholder Alignment

### D7 --- Developer Productivity & Operational Enablement (3 lessons)

-   D7-L01 Developer Productivity, Reusable Components and CI/CD
-   D7-L02 Production Deployment, Configuration and Operational
    Readiness
-   D7-L03 Hooks, Middleware and Controlled Extension Points

## 12. Lesson delivery and assessment

Every professional lesson includes observable learning outcomes,
prerequisites, executive orientation, first-principles explanation,
technical deep dive, architecture patterns and decision criteria,
diagram, worked example, implementation lab, trade-off analysis, failure
modes, security and governance, evaluation strategy, production
checklist, case study, knowledge checks, architect challenge, further
reading and key takeaways.

The Assessment Centre contains original knowledge checks and
rubric-based response prompts. Open-ended architectural judgement is
self-assessed against a visible answer guide; the local application does
not claim to provide an AI grader.

## 13. Deployment and data durability

The app can run locally without any paid AI API. For cross-device
learning on Streamlit Community Cloud, lesson content is deployed with
the GitHub repository and optional Supabase Postgres sync stores
progress, assessment attempts and imported question-bank records.
Configure the app password and Supabase credentials through Streamlit
secrets. The service-role key must remain server-side and must never be
committed to Git.

The included cloud sync is a single-owner personal deployment pattern.
It is not a multi-user identity system. For multi-user use, implement
Supabase Auth and per-user row-level security before inviting other
learners.

## 14. Release boundary and accuracy

The 29 lessons provide a comprehensive independent professional learning
curriculum, not official Anthropic exam content. No lesson contains
purported official exam questions. Model names, API features, protocol
behaviour, limits and exam objectives can change; verify
version-sensitive details against current primary documentation before
relying on them in a production design or examination response. The app
does not make live Claude or OpenAI calls and does not become a
generative AI tutor through this release.
