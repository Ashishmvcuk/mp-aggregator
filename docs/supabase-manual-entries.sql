-- Run in Supabase SQL Editor after creating a project.
--
-- If the table already exists without `enrollments`, alter the check constraint in the SQL editor
-- (drop the old CHECK on `category` and add one that includes `'enrollments'`), or recreate the table from this file.
-- Then: Authentication → Users → add user (email + password) for editors.

create table if not exists public.manual_entries (
  id uuid primary key default gen_random_uuid(),
  category text not null check (
    category in (
      'results',
      'news',
      'jobs',
      'syllabus',
      'admit_cards',
      'blogs',
      'enrollments'
    )
  ),
  university text not null,
  title text not null,
  link_url text not null,
  date text not null default '',
  created_at timestamptz not null default now()
);

create index if not exists manual_entries_category_idx on public.manual_entries (category);
create index if not exists manual_entries_created_idx on public.manual_entries (created_at desc);

alter table public.manual_entries enable row level security;

-- Anyone can read (published site merges these with scraped JSON).
create policy "manual_entries_select_public"
  on public.manual_entries
  for select
  using (true);

-- Only signed-in users can change rows (create editor accounts in Supabase Auth).
create policy "manual_entries_insert_authenticated"
  on public.manual_entries
  for insert
  to authenticated
  with check (true);

create policy "manual_entries_update_authenticated"
  on public.manual_entries
  for update
  to authenticated
  using (true)
  with check (true);

create policy "manual_entries_delete_authenticated"
  on public.manual_entries
  for delete
  to authenticated
  using (true);
