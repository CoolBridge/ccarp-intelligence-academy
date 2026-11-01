# Deploy CCAR-P Intelligence Academy to Streamlit Community Cloud

## What this deployment gives you
- A hosted URL that you can open from your phone, tablet, work computer or another laptop.
- Lessons and practice content are deployed from GitHub.
- Optional Supabase sync stores progress and assessment attempts outside the app filesystem.
- No OpenAI or Anthropic API key is required.

## Important storage distinction
Streamlit Community Cloud is a hosted app environment. Do not rely on the app's local SQLite file as durable cloud storage. This release supports optional Supabase Postgres sync. The app is designed for one private owner and uses an app password plus a server-side Supabase service-role key. Do not make the repository public with secrets in it, and do not share the access password.

## A. Create the cloud database (free tier)
1. Create a Supabase account and a new project.
2. Open the project's SQL Editor.
3. Run `deployment/supabase_setup.sql`.
4. In Project Settings / API, copy the Project URL and the `service_role` key. Keep the service-role key private.
5. The Supabase free tier is $0 but has quotas and inactivity pausing; check current plan limits before relying on it for important data.

## B. Upload the project to GitHub
1. Create a new private GitHub repository, for example `ccarp-intelligence-academy`.
2. Extract this ZIP on your computer.
3. Upload the contents of the `CCARP_Intelligence_Academy_Full` folder to the repository root (not the parent folder).
4. Confirm `app.py`, `requirements.txt`, `content/`, `.streamlit/config.toml` and `deployment/` are at the repository root.
5. Do not upload `.streamlit/secrets.toml`. The example file is safe because it contains placeholders only.

## C. Deploy with Streamlit Community Cloud
1. Sign in at https://share.streamlit.io/ using GitHub.
2. Choose **Create app** and select your repository, branch `main`, and main file path `app.py`.
3. Open **Advanced settings**.
4. Choose Python 3.12 (or another currently supported version).
5. Paste the contents of `.streamlit/secrets.toml.example` into the Secrets box, replacing the placeholders with your unique password, Supabase project URL and service-role key.
6. Click Deploy and wait for the app to start.
7. Restrict viewer access in the app settings if the option is available to your deployment. The in-app password is also required whenever cloud sync is configured.

## D. Verify cross-device learning
1. Open the hosted URL and enter your app password.
2. Open a professional lesson and save a mastery status and notes.
3. Open Assessment Centre and save an answer.
4. Refresh the app and confirm the data remains.
5. Open the same URL on your phone or another computer, sign in with the same app password and verify the same progress appears.

## E. Move existing laptop progress
Before deploying, open the current local academy and go to **Progress & Backup → Download academy backup**. Keep that JSON file somewhere safe. After configuring cloud sync and unlocking the hosted app, go to **Progress & Backup → Restore a previous academy backup**, upload the JSON file and click **Restore backup into this academy**. This imports progress, attempts and imported questions into the hosted database.

## F. Updating lessons later
The curriculum lives in `content/professional_lessons/`. Add or edit lesson JSON files, commit and push to GitHub. Streamlit Community Cloud rebuilds the app from the repository.

## Security notes
- The service-role key bypasses Supabase Row Level Security. It is used only server-side by this private, password-gated app.
- Never put the key in Python code, a public GitHub repository, screenshots or browser JavaScript.
- This simple single-owner design is not multi-user authentication. If you later share the academy with learners, redesign the data model around Supabase Auth and per-user row-level security.
- Do not use this study application to store sensitive personal, patient or confidential employer data.
