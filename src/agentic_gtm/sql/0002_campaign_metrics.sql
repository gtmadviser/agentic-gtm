create table if not exists campaign_metrics (
  id uuid primary key default gen_random_uuid(),
  provider text not null,
  campaign text not null,
  variant text not null default '',
  window_start timestamptz not null,
  window_end timestamptz not null,
  sent integer not null default 0,
  delivered integer,
  bounced integer not null default 0,
  replied integer not null default 0,
  positive_replies integer not null default 0,
  meetings integer not null default 0,
  opportunities integer not null default 0,
  source text not null default 'import',
  observed_at timestamptz not null default now(),
  unique (provider, campaign, variant, window_start, window_end)
);

alter table campaign_metrics enable row level security;
