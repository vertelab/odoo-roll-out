# Rollout App Coin Bridge

Pays coins into `gamification_coin` when a rollout app line is completed.

## What it does

The app records `coins_earned` on every completed line. This bridge gives
that number a destination: a credit in the coin ledger.

```
  rollout.app.line.done
        │
        ├── rollout_app_gamification ──► _add_karma(points_earned)
        │                                  (achievement — only goes up)
        │
        └── rollout_app_coin ──────────► _add_coins(coins_earned)
                                           (currency — can be spent)
```

Two bridges, two currencies, one completion event.

## Achievement vs. currency

This is the distinction the two bridges exist to keep:

| | Points → karma | Coins |
|---|---|---|
| Direction | Only up | Up and down |
| Drives | Rank, badges | A shop |
| Owned by | `gamification` | `gamification_coin` |

A person can spend every coin they have without their karma — or their rank
— moving at all. That is deliberate: karma is achievement, coins are money.

## Idempotence

Coins are credited **exactly once** per line. The guard is in the base
`_complete`: it returns `False` when the line is already `done`, and this
bridge only credits when it returns `True`. A re-run, a cron, or a double
trigger cannot credit twice.

Zero-coin lines are skipped entirely, so no empty ledger rows are created.

## Traceability

The ledger entry's `origin_ref` points back at the `rollout.app.line`, and
its `reason` names the task:

```
  gain    +5
  reason  "Completed: CRM kap 3 (Rollout App Line #42)"
  origin  rollout.app.line,42
```

So any coin movement can be traced to the task that earned it.

## Independence

| Direction | Depends on | Knows about |
|---|---|---|
| This bridge | `rollout_app`, `gamification_coin` | both |
| `gamification_coin` | `gamification` | **neither** |
| Shop (`gamification_coin_reward`) | `gamification_coin` | not this bridge |

The currency stays independent: it knows only that someone credited coins
and where from. This bridge knows nothing about the shop — a balance earned
before a shop exists is a plain number that a later consumer can use.

`auto_install` requires **both** parents. Without `gamification_coin` the
bridge does not install, and `coins_earned` remains a recorded number with no
destination — which is exactly what the app does on its own.

## Tests

```bash
sudo checkmodule -d test_db -m rollout_app,gamification_coin,survey,website_slides -t --drop
```

13 tests: crediting on completion, idempotence, zero-coin skip, the ledger
reason, traceability in both directions, that karma and coins move
independently, that coins do not touch karma or rank, and that the bridge has
no dependency on the shop.
