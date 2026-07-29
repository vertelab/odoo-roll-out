# Proposal: rollout-core

## Why

Organisationer som inför Odoo misslyckas oftare på grund av mänskliga faktorer än tekniska. Ingen existerande Odoo-modul hanterar *hela* förändringsresan — från beteendevetenskaplig analys och ISO-compliance till kompetensgap och scenarioplanering. Digital Adoption Platforms (WalkMe, Whatfix) är externa overlay-verktyg utan ERP-integration. Change management-plattformar (Prosci) saknar koppling till det system användarna faktiskt jobbar i. Odoos inbyggda gamification, LMS och HR-skills är kraftfulla men frånkopplade från varandra.

`rollout-core` fyller detta gap: en fristående Odoo-modul som orkestrerar beteendevetenskaplig verksamhetsförflyttning med ADKAR-metodik, riskhantering, kompetensstyrning, nudging, sentimentanalys och flerdimensionell plangranskning — helt inuti Odoo.

## What Changes

- **Ny fristående Odoo-modul**: `rollout` — beroenden endast `base` och `mail`. All integration med BPM, mgmtsystem, gamification, dashboard_vrtl och website_slides sker via bryggmoduler (`auto_install=True`).
- **14 nya modeller** som täcker hela förändringsresan:
  - `rollout.project` — flera parallella rollout-projekt med olika projektledare och organisationer
  - `rollout.phase` — ADKAR-faser med framåt-/bakåttidtabell och gates
  - `rollout.task` — checklista-items per fas
  - `rollout.role` — rollspecifika krav (kompetenser, kurser, badges)
  - `rollout.risk` — riskregister med probabilitet × impact, mitigation, trigger events
  - `rollout.scenario` — what-if-scenarier för alternativa tidslinjer
  - `rollout.sentiment` — pulsmätning med AI-analys av fritextsvar
  - `rollout.nudge` — beteendenudging med trigger → template-motor
  - `rollout.org_change` — organisationsförändringar som del av rollout
  - `rollout.competency.target` — kompetensmål: "3 personer med nivå X senast datum Y"
  - `rollout.competency.strategy` — strategier: intern/extern/träning/konsult per mål
  - `rollout.competency.scenario` — kompetensscenariopaket med kostnad, ledtid, risk
  - `rollout.plan.review` — flerdimensionell plangranskning (9 dimensioner, 42 kriterier)
  - `rollout.plan.review.criterion` — individuella granskningskriterier med scoring
- **Bryggmoduler**: `rollout_bpm`, `rollout_mgmtsystem`, `rollout_dashboard`, `rollout_gamification`, `rollout_lms` — aktiveras automatiskt när deras beroenden finns
- **Portfolio-vy**: `rollout.portfolio` — aggregerad CV-vy över medarbetarens skills, badges, kurser och adoption
- **Dashboard-vyer** (via `rollout_dashboard`-bryggan): adoption, sentiment heatmap, risk radar, scenario comparison, phase progress

## Capabilities

### New Capabilities

- `rollout-project`: Flera parallella rollout-projekt med projektledare, team, sponsorer, och ADKAR-faser. Oberoende av BPM, mgmtsystem, och gamification.
- `rollout-phase`: ADKAR-faser med två tidtabellslägen (framåt: "start X → klart Y", bakåt: "go-live X → vad innan?") och gates som blockerar nästa fas.
- `rollout-role`: Rollspecifika krav som kopplar kompetenser (hr.skill), kurser (slide.channel), badges (gamification.badge) och onboarding-checklistor.
- `rollout-risk`: Riskregister med probabilitet × impact, mitigation-planer, trigger events, ägare och state-tracking (identifierad → bevakas → inträffat → åtgärdat).
- `rollout-scenario`: Tidslinje-scenarier med alternativa start-/slutdatum, komprimerade faser, riskbedömning och kostnadsestimering.
- `rollout-sentiment`: Pulsmätning per projekt och användare. Fritextsvar analyseras med AI för hotspot-detection. Trendanalys över tid.
- `rollout-nudge`: Beteendenudging med trigger-regler (course_completed, login_streak, phase_transition) och mallbaserade meddelanden (social_proof, loss_aversion, default_nudge).
- `rollout-org-change`: Organisationsförändringar (nya avdelningar, omorganisation, nya roller, rapporteringslinjer) som del av rollout-projektet.
- `rollout-competency-target`: Kompetensmål — "X personer med kompetens Y på nivå Z senast datum D". Automatisk progress-tracking mot hr.employee.skill.
- `rollout-competency-strategy`: Strategier för att nå kompetensmål: intern omfördelning, extern rekrytering, kompetensutveckling, konsulter. Med kostnad, ledtid, och kopplingar till hr.job, slide.channel, hr.applicant.
- `rollout-competency-scenario`: Scenariopaket som grupperar strategier. Jämför kostnad, ledtid, och risk mellan scenarier.
- `rollout-plan-review`: Flerdimensionell plangranskning med 9 dimensioner (beteendevetenskap, risk, kompetens, tidplan, intressenter, ISO, org-förändring, budget, utbildning) och 42 fördefinierade kriterier. Genererar readiness-rapport med score 0-100.
- `rollout-portfolio`: Abstrakt modell som aggregerar medarbetarens kompetenser, kurser, badges och adoption till en CV-vy.

### Modified Capabilities

_Inga — detta är en helt ny modul med nya modeller._

## Impact

- **Ny kod**: `rollout/` — 14 modeller, views, security, data (fördefinierade granskningskriterier), demo
- **Nya dependencies**: `base`, `mail` (core Odoo). Inga externa beroenden.
- **Bryggmoduler** (i samma repo): `rollout_bpm/`, `rollout_mgmtsystem/`, `rollout_dashboard/`, `rollout_gamification/`, `rollout_lms/` — alla `auto_install=True`
- **Integrationer**: `hr.skill`, `hr.skill.level`, `hr.employee.skill` (core), `hr.job`, `hr.applicant` (core), `slide.channel` (core), `gamification.badge` (core), `survey.survey` (core), `mgmtsystem.*` (Vertel/OCA), `bpm.workflow` (Vertel), `dashboard.dashboard` (Vertel)
- **Påverkan på befintliga moduler**: Ingen — `rollout` ärver inget, modifierar inget. All koppling sker via bryggmoduler.
- **Licens**: AGPL-3
