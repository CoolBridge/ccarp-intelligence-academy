-- Run this once in the Supabase SQL Editor.
create table if not exists public.academy_records (
  record_key text primary key,
  owner_key text not null default 'primary',
  payload jsonb not null,
  updated_at timestamptz not null default now()
);
alter table public.academy_records enable row level security;

-- The app uses the service-role key only on the server side, stored in Streamlit secrets.
-- Never expose the service-role key in browser code or commit it to GitHub.
-- This single-owner table is intended for one private personal academy instance.
