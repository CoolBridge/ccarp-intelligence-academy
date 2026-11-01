# CCAR-P Intelligence Academy --- Full Edition 2.1

A local-first and cloud-deployable independent learning environment for
professional Claude architecture preparation.

## What is included

-   **29 professional lessons** across all seven domains.
-   **116 original knowledge checks** and rubric-based architect
    challenges.
-   Detailed written explanations, technical deep dives, Mermaid
    architecture flows, worked examples and Python implementation
    laboratories.
-   Architecture trade-off analysis, failure modes, security/governance,
    evaluation plans and production-readiness checklists.
-   The original 29 starter concept records as a supplementary revision
    layer.
-   Seven-domain learning path, assessment centre, mastery tracking,
    guided curriculum retrieval tutor, voice reader, question-bank
    import/export and JSON backup/restore.
-   Optional Supabase Postgres cloud sync for progress, assessment
    attempts and imported questions.
-   No paid OpenAI or Anthropic API is required.

## Run locally

1.  Extract the ZIP.
2.  Open the extracted `CCARP_Intelligence_Academy_Full` folder in VS
    Code.
3.  Open Terminal → New Terminal.
4.  Run:

``` bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

5.  Open `http://localhost:8501`.

The app requires Python 3.10+ and internet for initial package
installation. No model API key is required.

## Deploy for cross-device access

Read `deployment/STREAMLIT_CLOUD_DEPLOYMENT.md`.

-   Push the project to a GitHub repository.
-   Deploy `app.py` through Streamlit Community Cloud.
-   Configure the optional Supabase database and Streamlit secrets to
    persist progress across devices.
-   Export a backup from the old local app and restore it in the hosted
    app.

**Important:** Without external cloud sync, the hosted app's local
SQLite filesystem must not be treated as durable. The included cloud
sync is a single-owner personal deployment protected by an app password.
It is not a multi-user authentication system.

## Curriculum

See `docs/PROFESSIONAL_LESSON_SPECIFICATION.md` for the lesson standard
and complete 29-lesson inventory.

  Domain                                                      Professional lessons
  --------------------------------------------------------- ----------------------
  D1 --- Solution Design & Architecture                                          6
  D2 --- Claude Models, Prompting & Context Engineering                          4
  D3 --- Integration & Tool Use                                                  4
  D4 --- Evaluation, Testing & Optimisation                                      5
  D5 --- Governance, Safety & Risk Management                                    3
  D6 --- Stakeholder Communication & Lifecycle Management                        4
  D7 --- Developer Productivity & Operational Enablement                         3
  **Total**                                                                 **29**

## Accuracy and limitations

This is an independent study aid, not an Anthropic product or official
exam platform. The questions are original practice material, not
official or leaked examination questions. The guided tutor retrieves
from local curriculum content; it is not a live generative AI model.
Open-ended assessment responses are saved for self-assessment against
visible answer guides; the app does not claim to provide an AI grader.
Verify current exam objectives, model behaviour, API details and
protocol features against current primary documentation.

## Privacy and security

Do not store patient data, confidential employer records, credentials or
other sensitive information in this study app. Keep
`.streamlit/secrets.toml` out of Git. Never expose the Supabase
service-role key in source code, browser code or a public repository.
