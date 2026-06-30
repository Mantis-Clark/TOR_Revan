# TOR_Revan — Act I Player Guide
### "Ghosts of the Past"

Act I adapts the opening of the *Revan* novel (Prologue + Ch. 1–7). It follows **two
protagonists** whose stories run in parallel and eventually converge:

- **Revan** — two years after the war, hailed as a hero but haunted by fragments of memory
  he cannot place. A visit from an old comrade pulls him back onto the trail of a nameless enemy.
- **Lord Scourge** — a Sith warrior on Dromund Kaas, caught in the deadly politics of the
  Dark Council, who begins to sense a threat far greater than the rivalries around him.

> Everything in this mod is a fan adaptation built on reused KOTOR II assets. Areas and several
> character appearances are **stand-ins** (noted below); the writing is original.

---

## Before you start

1. **Enable cheats** (already done): `swkotor2.ini` → `[Game Options]` → `EnableCheats=1`.
2. Open the **console** in-game with the **`** key (backquote/tilde). Commands are typed blind.
3. Optional — kit out as Revan first (see **Items**).

The console commands you'll use:
- `warp <module>` — jump to an area.
- `giveitem <code>` — add an item.

---

## The Revan thread (the main playthrough)

This is wired as one continuous flow. Start it with a single command:

> **`warp tor_coru`**

### 1 — Coruscant, the Dealer's Den
A back-alley cantina in the galactic capital. Find **Mandalore** and speak with him.

- He reveals himself as **Canderous Ordo** — your companion from the war, now wearing the
  Mandalore mask (*not* Mandalore the Ultimate, who fell at Malachor).
- He brings the lead: old **Mandalorian relics** that speak of an enemy the Republic never names —
  perhaps the face behind your nightmares.
- Choose **"Then we leave together. Tell me where."** to set out.

➡️ This **starts the quest "The Hunt"** and **transports you to the Ebon Hawk**.

### 2 — The Ebon Hawk (hub)
Your ship and travel hub. Speak with **Mandalore** again and **set course**.

➡️ The journal updates and you **jump to the dead world**.

### 3 — The Dead World (Nathema)
A world drained of all life and the Force. At its heart waits **the Sith Emperor**.

- Approach and speak with him — a branching confrontation about your stolen memory and his ambition.
- Choose **"Then I will end this here…"** to **trigger the fight**. Defeating him completes the
  final stage of *The Hunt*.
- **POV party:** on arrival you are joined by **Lord Scourge** and **Meetra Surik**. Switch which
  one you control using the **party panel** (the protagonist-switching framework — see below).

---

## The Scourge thread (parallel intro)

Played separately for now (it converges with Revan's story in later acts):

> **`warp tor_kaas`**

**Dromund Kaas — a Sith stronghold.** Report to your master, **Darth Nyriss** of the Dark Council.
She probes your loyalty and hints that something hidden moves beneath the Council's schemes — the
first thread of the conspiracy Scourge will unravel.

---

## Playing as Revan — Items

| Item | Code | Effect |
|---|---|---|
| Revan's Robes | `giveitem tor_revanrobe` | Equip → become **Darth Revan** (masked) |
| Revan's Jedi Robes | `giveitem tor_revanjedi` | Equip → become **Jedi Revan** (unmasked, novel-accurate) |
| Revan's Lightsaber | `giveitem tor_revsaber` | A custom hilt with full blade + ignition |

Equip the robes and the saber to play the whole flow **as Revan**.

---

## The 3-POV switching framework

At the confrontation (`tor_nath`), your party contains all three protagonists — **Revan, Lord
Scourge, Meetra Surik**. Use the in-game **party UI** to switch who you control. This is the
foundation for the full adaptation, where each act hands control to its protagonist.

---

## Quest log

**"The Hunt"** tracks your progress through the Revan thread:
1. Mandalore's lead, aboard the Ebon Hawk.
2. Arrival at the dead world.
3. The confrontation at its heart *(completes the Act I stage).* 

Open your **Journal** to read each update.

---

## Stand-ins & known caveats

- **Areas** are reused KOTOR II geometry: the Dealer's Den is a Telos cantina, the Sith
  stronghold is a Trayus/Sith interior, the dead world is the Korriban academy. Bespoke dressing
  comes later.
- **Appearances**: the Emperor uses Darth Nihilus's model; Scourge and Meetra use robed stand-ins
  (KOTOR has no Sith-Pureblood or Exile model); Mandalore and Nyriss use their closest vanilla looks.
- This is an in-development vertical slice — transitions, the journal, and the POV party are new
  systems and may need tuning. Report anything that misbehaves.

---

## Quick reference

| Goal | Command |
|---|---|
| Start the Revan playthrough | `warp tor_coru` |
| Scourge intro | `warp tor_kaas` |
| Jump straight to the confrontation | `warp tor_nath` |
| Become Jedi Revan | `giveitem tor_revanjedi` |
| Become Darth Revan | `giveitem tor_revanrobe` |
| Get Revan's saber | `giveitem tor_revsaber` |
