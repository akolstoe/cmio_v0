# CMIO Data Model Overview

This document explains how the SQLAlchemy models defined in `models.py` enable the
Unified Communication Hub, Real-Time Information Extractor, Two-Step Documentation
Engine, and Morning Dashboard experiences.

## Message Capture
- `Message` stores channel, direct, and note-to-self communications using the
  `MessageType` enum.
- `TeamChannel` and `User` provide the collaboration context.
- The `message_clients` association links any message to zero or more clients so
  downstream features always know which records were referenced.

## Pending Facts and Audit Trail
1. When the regex/AI extractors run, each detected data point becomes a `PendingFact`.
2. `PendingFact.source_message_id` keeps the pointer to the exact message text.
3. When a human approves an item, the workflow creates a `ClientFact` row that:
   - copies the value and security rating,
   - records `approved_by_id` and `approved_at`, and
   - keeps `pending_fact_id` so every approved fact remains traceable to the
     pending review state and original message.
4. `ModelRun` tracks which AI/regex configuration produced each pending fact or
   message analysis, giving us end-to-end observability.

Because a `ClientFact` references the `PendingFact`, which references the
`Message`, we always have a full audit trail from finalized client information
back to the original conversation.

## Encounter Notes → Case Notes
- `EncounterNote` represents the auto-drafted documentation that originates from
  a specific message trigger (`source_message_id`).
- Once reviewed, each encounter note spawns exactly one `CaseNote` (`CaseNote`
  keeps a unique FK to `EncounterNote`). This enforces the two-step flow while
  maintaining the linkage to the client, author, and finalized text.

## Client Profiles and Security Layers
- `Client` stores identity and engagement preferences.
- `ClientFact.security_rating` ensures that every approved data point carries a
  classification (`shared`, `sensitive`, `private`) that downstream UI workflows
  can respect.

## Task Breakdown System
- `Task` ties to a client (optional) and stores owner, due dates, and estimates.
- `TaskStep` decomposes the work into bite-sized, time-estimated steps to feed
  the Morning Dashboard planner.
