-- Preserve snapshot semantics and reserve plans before provider writes.
alter table action_plans drop constraint if exists action_plans_status_check;
alter table action_plans add constraint action_plans_status_check
  check (status in ('pending', 'applying', 'needs_review', 'applied', 'expired'));

alter table campaign_metrics add column if not exists campaign_id text;
alter table campaign_metrics add column if not exists kind text not null default 'interval';
alter table campaign_metrics add column if not exists unit text not null default 'email';
update campaign_metrics set campaign_id = campaign where campaign_id is null;
alter table campaign_metrics alter column campaign_id set not null;
alter table campaign_metrics alter column replied drop not null;
alter table campaign_metrics alter column positive_replies drop not null;
alter table campaign_metrics alter column meetings drop not null;
alter table campaign_metrics alter column opportunities drop not null;
alter table campaign_metrics alter column replied drop default;
alter table campaign_metrics alter column positive_replies drop default;
alter table campaign_metrics alter column meetings drop default;
alter table campaign_metrics alter column opportunities drop default;
-- Historical Instantly imports used cumulative counts and mislabeled opportunities
-- as positive replies. The original payload did not preserve unique human replies.
update campaign_metrics set kind = 'cumulative', positive_replies = null,
  meetings = null, replied = null, source = 'instantly.analytics.legacy'
  where source = 'instantly.analytics' and kind = 'interval';
-- Find the original generated unique-constraint name (Postgres truncates names).
do $$ declare item record; begin
  for item in select conname from pg_constraint
    where conrelid = 'campaign_metrics'::regclass and contype = 'u'
  loop execute format('alter table campaign_metrics drop constraint %I', item.conname); end loop;
end $$;
create unique index if not exists campaign_metrics_identity
  on campaign_metrics(provider, campaign_id, variant, kind, unit, window_start, window_end);
