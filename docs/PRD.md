# Product Requirements Document
# KickLoad — Football Gathering App

**Version:** 0.1  
**Status:** Draft  
**Author:** Puvanat  
**Last Updated:** 2026-05-08

---

## 1. Problem Statement

Thai casual football players have no dedicated tool to:
- Find open matches nearby when they want to play spontaneously
- Fill incomplete team rosters quickly
- Match with players of similar skill level
- Find available stadiums near them
- Track weekly win records within their group
- Manage shared field cost payments fairly

No equivalent product exists in the Thai market as of 2026.

---

## 2. Target User

**Primary:** Thai male, age 18–35, plays casual or semi-regular football  
**Secondary:** Stadium owners who want to increase booking utilization  
**Geography:** Thailand only (Phase 1)  
**Language:** Thai (primary), English (secondary)

**User behaviors to design for:**
- Uses LINE more than any other messaging platform
- Pays via PromptPay, not credit card
- Plans football on short notice (same day or 1–2 days ahead)
- Plays in groups of friends ("gang") that meet weekly

---

## 3. Features (Phase 1 — MVP)

### F1: Match Discovery (Find a Game)
A solo player can browse open matches within a configurable radius, filtered by:
- Distance from current location
- Match format (5v5, 7v7, 11v11)
- Skill level range (ELO-based)
- Start time
- **Open position matching** — only show matches where an open slot matches the player's preferred positions

**Success metric:** Player finds and joins a match within 3 taps.

---

### F2: Team Roster Filling
A team captain can create a match with declared position slots. The match is discoverable until all slots are filled.

- Captain declares: format, time, stadium, positions needed per team
- Each position slot shows: required role, filled/open status
- System sends push notification to nearby players who match open positions

**Success metric:** Average time-to-fill drops below 2 hours for 5v5 matches.

---

### F3: Skill-Level Matching (ELO System)
Every player has an ELO rating starting at 1,000. Rating updates after each submitted game result.

- Match creation has a skill range (e.g., 900–1,100)
- Players outside the range cannot join
- ELO formula: `new_rating = old_rating + K * (actual - expected)`
  - K = 32 for players under 20 games played, K = 16 otherwise
  - Win = 1, Draw = 0.5, Loss = 0

**Out of scope (Phase 1):** Manual skill self-assessment, referee verification.

---

### F4: Stadium Finder
Players can search for available stadiums near them.

- Stadium owners register venue with: name, address, lat/lon, surface type (grass/futsal/turf), price/hour, available time slots, photos
- Search filters: distance, price range, surface type, available time
- Booking: reserve a time slot (simple lock — no payment gateway to stadium yet)

**Success metric:** Stadium search returns results within 10 km for 80% of Bangkok users.

---

### F5: Gang Leaderboard
A "gang" is a recurring group of players (e.g., office colleagues who play every Sunday).

- Any player can create a gang and invite others via link or LINE
- After each match, captain submits the result
- App tracks: wins, losses, draws, goals scored per player within the gang
- Leaderboard resets per season (configurable: weekly / monthly)

**Success metric:** At least one result submitted per gang per week for active gangs.

---

### F6: Payment Splitting
Field cost is split between teams. Within each team, the treasurer tracks individual payments.

- Match creator sets total field cost
- System calculates: cost per team, cost per player (equal split)
- Each team designates a treasurer
- Treasurer confirms when team has paid the field owner (external, via PromptPay)
- Players mark themselves as paid to the treasurer
- App shows: [paid ✓] / [unpaid ✗] list visible to all team members

**Out of scope (Phase 1):** Automated PromptPay integration, in-app transfers.

---

## 4. Out of Scope (Phase 1)

- Tournament brackets or league management
- Live match streaming or score commentary
- In-app payments or PromptPay QR generation
- Referee or coach profiles
- Betting or prediction features
- Outside Thailand

---

## 5. Technical Constraints

- Mobile-first (iOS and Android)
- Must work on 4G (optimize for low-bandwidth rural areas)
- Thai language UI required at launch
- LINE Login required (primary auth method for Thai users)
- Location permission required for core features

---

## 6. Success Metrics (3-Month Targets)

| Metric | Target |
|---|---|
| Registered users | 500 |
| Matches created | 200 |
| Matches with all slots filled | 60% |
| Weekly active users | 150 |
| Average session length | > 3 minutes |
| Gang leaderboards created | 50 |

---

## 7. Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Low stadium supply in early markets | High | Manually onboard 10 stadiums in Bangkok before launch |
| Players don't submit game results (kills leaderboard) | Medium | Make result submission the only way ELO updates — social incentive |
| ELO manipulation (throw games) | Low | Flag accounts with unusual rating swings for review |
| PromptPay slip verification fraud | Low | Phase 1 is trust-based; verification via OCR in Phase 2 |
