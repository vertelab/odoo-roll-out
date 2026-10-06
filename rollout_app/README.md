# Rollout App

The daily entry point for a rollout participant: a short, personal menu of
things to do, points for doing them, and a weekly rhythm.

Where `rollout_internal` shows plain lists, this module provides the loop:
**action → points → recognition**.

## The data model

Three models, no template level.

```
  rollout.module            a content type — the contract
        │
        ▼
  rollout.module_line       an instance of that type
        │
        ▼   one row per person
  rollout.app.line          that person's outcome

  rollout.app               the project's menu
```

| Model | Is |
|---|---|
| `rollout.module` | "Kurs", "Enkät", "Referens" — owns what its lines may point at |
| `rollout.module.line` | "CRM kap 3", "Veckans enkät v.41" |
| `rollout.app` | The project's menu. One per project |
| `rollout.app.line` | One person's status, points and source for one line |

The team is the project's `team_member_ids`. There is no separate team model.

## Configuring a module type

| Field | Meaning |
|---|---|
| `allowed_model` | The only model this type's lines may reference, e.g. `slide.channel`. Empty = anything (for manual, self-reported types) |
| `spawn_mode` | `static` (exists from configuration, waits until done) or `periodic` (a new line each period) |
| `recurrence` | `daily` / `weekly` / `monthly`. Required for periodic |
| `lead_time` | How many periods ahead the spawn cron creates lines |
| `clear_mode` | `auto` (read the source model), `manual` (the person reports it), or `either` |
| `default_points` / `default_coins` | Inherited by lines unless overridden |

**Static** is for a course list: the list is constant, and a row waits until
it is done. **Periodic** is for a survey: a new line is created each period,
and the line leaves the view when the period ends.

## Configuring a line

| Field | Meaning |
|---|---|
| `module_id` | The type. Points and coins are inherited from it |
| `module_rel` | The record this line points at, e.g. `(slide.channel, 4)` |
| `state` | `locked` / `open` / `done` — line-level, for lines concluded for everyone |
| `period_start` / `period_end` | The line's period |
| `publish_at` | When the line becomes visible |
| `remind_at` | When a reminder is evaluated if still open |
| `source_line_id` | The line whose completion unlocks this one |
| `unlock_badge_id` | The badge that unlocks this one |
| `badge_id` | Displayed as the reward. **Never awarded by this module** |

### Periods and publishing times

The spawn cron runs daily and creates the next period's line for every
periodic type, `lead_time` periods ahead. It sets:

- `period_start` — the first day of the period (Monday for weekly)
- `period_end` — the last day
- `publish_at` — **07:00 on the first day**
- `remind_at` — **07:00 three days later**

So a weekly line is created on Sunday evening and appears in the menu at
07:00 on Monday. The cron is idempotent per `(module_id, period_start)`: a
second run in the same period creates nothing.

To change the publishing time, edit the line after it is spawned, or adjust
`cron_rollout_app_spawn` in `models/rollout_module_line.py`.

## The two states

`rollout.app.line.state` has exactly two values: `open` and `done`.

There is **no `missed` state**. "Missed" is a question asked of the data:

```python
lines = env['rollout.app.line'].search(
    env['rollout.app.line']._missed_domain(user))
# open AND period_end < today
```

A line whose period has ended leaves the view but stays in data, so the
weekly summary can still report on it.

## Points and coins

Completing a line awards `points_earned` and `coins_earned`, taken from the
module line. Awarded **exactly once** — `_complete` returns early when the
line is already done, so a double trigger or a cron re-run cannot award
twice.

- **Points** → karma, via `rollout_app_gamification` (if gamification is installed)
- **Coins** → a spendable balance, via `rollout_app_coin` (if installed)

The app records both on `rollout.app.line` regardless, so the totals work
even without either bridge installed.

## Gamification

`rollout_app_gamification` (auto-install) connects completions to Odoo's
gamification:

- karma is awarded via `res.users._add_karma`, once per line;
- a locked advanced line gated on a completed line is unlocked, **per person**.

**Badges are never created by this module.** `badge_id` on a line is a
display link; the badge itself is granted by gamification's own rules.

## Nudges

Three new `trigger_event` values reuse the existing nudge engine — there is
no separate trigger motor:

| Event | Fired |
|---|---|
| `period_published` | When a period's line is spawned |
| `still_open` | At `remind_at`, if the person's line is still open |
| `line_completed` | On completion, for celebration and unlock announcements |

The `still_open` nudge can include the team's completion count, so the
reminder carries social proof ("7 av 10 har svarat").

## PWA and Web Push

| Endpoint | Serves |
|---|---|
| `/rollout_app/manifest.json` | The web app manifest |
| `/rollout_app/service-worker.js` | The service worker, with `Service-Worker-Allowed: /` |
| `/rollout_app/subscribe` | Stores a push subscription |
| `/rollout_app/unsubscribe` | Deactivates one |
| `/rollout_app/vapid_public_key` | The VAPID public key for the browser |

The service worker is served from Odoo's origin because Web Push requires it.
The `Service-Worker-Allowed: /` header widens its scope so it can handle
pushes for the whole backend.

### VAPID keys

Push needs a VAPID key pair. Set them as system parameters:

```
rollout_app.vapid_public_key    the public key (sent to the browser)
rollout_app.vapid_private_key   the private key (never leaves the server)
rollout_app.vapid_subject       mailto: or https: — required by the spec
rollout_app.push_daily_max      max pushes per user per day (default 3)
```

Generate a pair once:

```bash
python3 -c "
from py_vapid import Vapid
v = Vapid()
v.generate_keys()
print('public :', v.public_key.public_bytes(
    __import__('cryptography.hazmat.primitives.serialization',
               fromlist=['Encoding']).Encoding.X962,
    __import__('cryptography.hazmat.primitives.serialization',
               fromlist=['PublicFormat']).PublicFormat.UncompressedPoint
).hex())
"
```

**Rotating keys invalidates every existing subscription.** A subscription is
bound to the key that created it. After a rotation:

1. set the new keys;
2. deactivate all subscriptions — they will never succeed again:
   ```python
   env['rollout.push.subscription'].search([]).active = False
   ```
3. users re-subscribe on their next visit.

Never rotate without step 2: the server would keep sending to endpoints that
can only fail.

### Dead subscriptions

When the push service answers HTTP 404 or 410, the subscription is
deactivated automatically. Retrying a gone endpoint only wastes time.

### iOS

Web Push on iOS requires the app to be **installed to the home screen**. In a
Safari tab it does not work at all. The app detects this and explains how to
install rather than offering a button that would fail.

## Tests

```bash
checkmodule -d test_db -m rollout_app,survey,website_slides -t --drop
```

44 tests: module types and validation, line creation and the `allowed_model`
gate, generation and idempotence, completion and point idempotence, the
locked-line guard, personal and team aggregation, period visibility and the
missed query, access control, the spawn cron, karma and per-person unlocking,
badge non-creation, and the push queue with its anti-spam cap.

## Known issue in `rollout_internal`

`rollout_internal/models/rollout_nudge.py` has two defects that predate this
module and are **not fixed here** (they are outside this change):

1. `fields` was used without being imported — fixed, since it broke every
   `_deliver_simple` call;
2. `mail.activity` is created without `res_model_id`/`res_id`, which Odoo
   requires. This still fails on every call.

The push tests call `_stage_push` directly rather than going through
`_deliver_simple`, so they do not depend on that broken path.
