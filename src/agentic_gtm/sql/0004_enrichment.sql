-- All monetary values are integer micro-USD upper bounds, never invoice totals.
create table if not exists enrichment_runs (
  run_id text primary key,
  plan jsonb not null,
  requests integer not null default 0,
  reserved_microusd bigint not null default 0
);
create table if not exists enrichment_cache (
  cache_key text primary key,
  call_id text not null,
  status text not null check (status in ('pending', 'ready', 'uncertain')),
  response jsonb,
  observed_at timestamptz,
  expires_at timestamptz
);
create table if not exists enrichment_calls (
  call_id text primary key,
  run_id text not null references enrichment_runs(run_id),
  cache_key text not null,
  body jsonb not null
);
create index if not exists enrichment_calls_run on enrichment_calls(run_id);
alter table enrichment_runs enable row level security;
alter table enrichment_cache enable row level security;
alter table enrichment_calls enable row level security;
grant select, insert, update on enrichment_runs, enrichment_cache, enrichment_calls to service_role;

create or replace function gtm_enrichment(p_operation text, p_data jsonb)
returns jsonb language plpgsql security invoker set search_path = public as $$
declare
  r enrichment_runs;
  c enrichment_cache;
  l enrichment_calls;
  price bigint;
  v_body jsonb;
begin
  if p_operation = 'register' then
    if coalesce(p_data->>'client_id', '') = '' or coalesce(p_data->>'account_scope', '') = ''
       or coalesce(p_data->>'provider', '') = '' or coalesce(p_data->>'price_basis', '') = ''
       or coalesce(p_data->>'run_id', '') = ''
       or coalesce(p_data->>'plan_hash', '') !~ '^[a-f0-9]{64}$'
       or coalesce((p_data->>'max_calls')::integer, 0) not between 1 and 10000
       or coalesce((p_data->>'budget_microusd')::bigint, 0) <= 0
       or jsonb_typeof(p_data->'prices_microusd') is distinct from 'object'
       or p_data->'prices_microusd' = '{}'::jsonb then
      raise exception 'Invalid paid run';
    end if;
    if exists (select 1 from jsonb_each_text(p_data->'prices_microusd') x
               where x.value !~ '^[0-9]+$' or x.value::bigint <= 0) then
      raise exception 'Endpoint prices must be positive micro-USD upper bounds';
    end if;
    insert into enrichment_runs(run_id, plan) values (p_data->>'run_id', p_data)
      on conflict do nothing;
  end if;
  select * into r from enrichment_runs where run_id = p_data->>'run_id' for update;
  if not found then raise exception 'Paid run is not registered'; end if;
  if p_operation = 'register' then
    if r.plan <> p_data then raise exception 'Paid run already exists with another immutable plan'; end if;
    return jsonb_build_object('plan', r.plan, 'requests', r.requests,
      'reserved_microusd', r.reserved_microusd);
  elsif p_operation = 'inspect' then
    return jsonb_build_object('plan', r.plan, 'requests', r.requests,
      'reserved_microusd', r.reserved_microusd, 'ledger',
      coalesce((select jsonb_agg(body order by call_id) from enrichment_calls where run_id = r.run_id), '[]'::jsonb));
  elsif p_operation = 'reserve' then
    -- Serialize the same cache identity even when two different runs request it.
    perform pg_advisory_xact_lock(hashtextextended(p_data->>'cache_key', 0));
    select * into c from enrichment_cache where cache_key = p_data->>'cache_key' for update;
    if found and c.status <> 'ready' then
      raise exception 'Previous paid call is pending or uncertain; reconcile before reuse';
    end if;
    v_body := p_data || jsonb_build_object('status', 'pending', 'cost_source', 'accepted_upper_bound');
    if c.status = 'ready' and c.expires_at > (p_data->>'now')::timestamptz then
      v_body := v_body || jsonb_build_object('status', 'cache_hit', 'reserved_microusd', 0,
        'cost_source', 'cache', 'observed_at', c.observed_at);
      insert into enrichment_calls values (p_data->>'call_id', r.run_id, p_data->>'cache_key', v_body);
      return to_jsonb(c) || jsonb_build_object('action', 'cache_hit');
    end if;
    price := (r.plan->'prices_microusd'->>(p_data->>'endpoint'))::bigint;
    if price is null or price <= 0 then raise exception 'Endpoint is outside the accepted pricing plan'; end if;
    if r.requests >= (r.plan->>'max_calls')::integer then raise exception 'Accepted request cap reached'; end if;
    if r.reserved_microusd + price > (r.plan->>'budget_microusd')::bigint then
      raise exception 'Accepted spend ceiling would be exceeded';
    end if;
    update enrichment_runs set requests = requests + 1, reserved_microusd = reserved_microusd + price
      where run_id = r.run_id;
    v_body := v_body || jsonb_build_object('reserved_microusd', price);
    insert into enrichment_calls values (p_data->>'call_id', r.run_id, p_data->>'cache_key', v_body);
    insert into enrichment_cache(cache_key, call_id, status)
      values (p_data->>'cache_key', p_data->>'call_id', 'pending')
      on conflict (cache_key) do update set call_id = excluded.call_id, status = 'pending',
        response = null, observed_at = null, expires_at = null;
    return '{"action":"execute"}'::jsonb;
  elsif p_operation = 'finish' then
    select * into l from enrichment_calls where call_id = p_data->>'call_id' for update;
    if not found or l.run_id <> r.run_id or l.cache_key <> p_data->>'cache_key' then
      raise exception 'Unknown paid-call reservation';
    end if;
    if l.body->>'status' <> 'pending' then raise exception 'Paid-call reservation already completed'; end if;
    if p_data->>'status' is null or p_data->>'status' not in ('success', 'uncertain') then
      raise exception 'Invalid completion status';
    end if;
    update enrichment_calls set body = body || jsonb_build_object('status', p_data->>'status')
      where call_id = l.call_id;
    update enrichment_cache set
      status = case when p_data->>'status' = 'success' then 'ready' else 'uncertain' end,
      response = p_data->'response', observed_at = (p_data->>'observed_at')::timestamptz,
      expires_at = (p_data->>'expires_at')::timestamptz
      where cache_key = l.cache_key and call_id = l.call_id;
    return jsonb_build_object('status', p_data->>'status');
  end if;
  raise exception 'Unknown enrichment operation';
end;
$$;
revoke all on function gtm_enrichment(text, jsonb) from public, anon, authenticated;
grant execute on function gtm_enrichment(text, jsonb) to service_role;
