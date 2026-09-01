create extension if not exists pgcrypto;

create table if not exists accounts (
  id uuid primary key default gen_random_uuid(),
  provider text not null,
  provider_id text not null,
  source_url text,
  observed_at timestamptz not null default now(),
  name text not null,
  domain text,
  industry text,
  employee_count integer,
  country_code text,
  attributes jsonb not null default '{}'::jsonb,
  unique (provider, provider_id)
);

create table if not exists contacts (
  id uuid primary key default gen_random_uuid(),
  provider text not null,
  provider_id text not null,
  source_url text,
  observed_at timestamptz not null default now(),
  account_id uuid references accounts(id),
  full_name text not null,
  title text,
  email text,
  linkedin_url text,
  attributes jsonb not null default '{}'::jsonb,
  unique (provider, provider_id)
);

create table if not exists opportunities (
  id uuid primary key default gen_random_uuid(),
  provider text not null,
  provider_id text not null,
  source_url text,
  observed_at timestamptz not null default now(),
  account_id uuid references accounts(id),
  name text not null,
  stage text not null,
  status text not null check (status in ('open', 'won', 'lost')),
  amount numeric,
  currency text,
  close_date timestamptz,
  attributes jsonb not null default '{}'::jsonb,
  unique (provider, provider_id)
);

create table if not exists activities (
  id uuid primary key default gen_random_uuid(),
  provider text not null,
  provider_id text not null,
  source_url text,
  observed_at timestamptz not null default now(),
  account_id uuid references accounts(id),
  contact_id uuid references contacts(id),
  opportunity_id uuid references opportunities(id),
  kind text not null,
  occurred_at timestamptz not null,
  summary text,
  attributes jsonb not null default '{}'::jsonb,
  unique (provider, provider_id)
);

create table if not exists evidence (
  id uuid primary key,
  subject text not null,
  claim text not null,
  kind text not null check (kind in ('declared', 'observed', 'hypothesis', 'decision')),
  source text not null,
  observed_at timestamptz not null,
  confidence numeric not null check (confidence between 0 and 1),
  supports boolean not null
);

create table if not exists experiments (
  id uuid primary key,
  body jsonb not null,
  status text not null,
  updated_at timestamptz not null default now()
);

create table if not exists campaign_drafts (
  id uuid primary key,
  provider text not null,
  body jsonb not null,
  status text not null check (status in ('draft', 'paused')),
  updated_at timestamptz not null default now()
);

create table if not exists campaigns (
  id uuid primary key default gen_random_uuid(),
  provider text not null,
  provider_id text not null,
  observed_at timestamptz not null default now(),
  body jsonb not null,
  unique (provider, provider_id)
);

create table if not exists metric_snapshots (
  id uuid primary key,
  metric text not null,
  numerator numeric not null,
  denominator numeric not null,
  window_start timestamptz not null,
  window_end timestamptz not null,
  dimensions jsonb not null default '{}'::jsonb
);

create table if not exists sync_cursors (
  provider text not null,
  stream text not null,
  cursor jsonb not null,
  updated_at timestamptz not null default now(),
  primary key (provider, stream)
);

create table if not exists action_plans (
  id uuid primary key,
  operation text not null,
  provider text not null,
  targets jsonb not null,
  payload jsonb not null,
  payload_summary text not null,
  idempotency_key text not null unique,
  created_at timestamptz not null,
  expires_at timestamptz not null,
  hash text not null,
  status text not null check (status in ('pending', 'applied', 'expired'))
);

create table if not exists apply_results (
  plan_id uuid primary key references action_plans(id),
  provider text not null,
  status text not null,
  provider_ids jsonb not null,
  verified boolean not null,
  message text not null,
  applied_at timestamptz not null
);

alter table accounts enable row level security;
alter table contacts enable row level security;
alter table opportunities enable row level security;
alter table activities enable row level security;
alter table evidence enable row level security;
alter table experiments enable row level security;
alter table campaign_drafts enable row level security;
alter table campaigns enable row level security;
alter table metric_snapshots enable row level security;
alter table sync_cursors enable row level security;
alter table action_plans enable row level security;
alter table apply_results enable row level security;
