# Teacher-Facing Tools for Early-Grade Reading in Low-Resource Classrooms
## Research Survey: Design Implications for an Offline Urdu Reading App

**Date:** 2026-09-18  
**Purpose:** Feature specification and workflow design for teacher mode of offline Urdu reading app  
**Scope:** Classroom assessment (EGRA-style), lesson planning/delivery, learner grouping, progress tracking, and home tutor support

---

## 1. Context: What Teachers Actually Need

### Classroom Scenario (Primary Use Case)
- **Environment:** One teacher, ~30 children, shared tablet (no projector)
- **Time constraint:** 40-minute lesson block
- **Connectivity:** Offline-first (intermittent internet)
- **Device:** Low-cost Android tablet (4-8GB RAM, modest processor)
- **Grouping model:** Ability to group children by reading level and rotate instruction

### Home Tutor Scenario (Secondary Use Case)
- **Audience:** Diaspora parents, heritage language tutors in homes abroad
- **Constraint:** Non-specialist tutors (not trained teachers)
- **Device:** Shared family tablet or phone
- **Goal:** Child maintains Urdu literacy; parent can track progress and adjust difficulty

---

## 2. Existing Tools Landscape

### A. EGRA-Optimized Tablet Tools

#### **Tangerine (RTI International)**
- **Type:** Offline-first EGRA assessment platform (open-source)
- **Deployment:** 5M+ assessments across 65+ countries in 100+ languages
- **Key features:**
  - Built-in timer (replaces manual stopwatch)
  - One-to-one timed reading assessment workflow
  - Auto-scoring on tablet (no manual marking after test)
  - Immediate class-level reports (pass/fail by subtask, fluency comparison)
  - Offline data sync: store on tablet, upload when connected
  - Android-native (optimized for low-cost devices)
- **Teacher UX:** Minimal: tap start → read timer display → tap when student finishes each subtask
- **Assessment scope:** EGRA subtasks (letter ID, oral fluency, comprehension)
- **Status:** Production-ready, used in 65+ countries

**Source:** https://www.rti.org/impact/tangerine-mobile-reading-mathematics-assessments; https://www.tangerinecentral.org/

#### **Kolibri Coach (Learning Equality)**
- **Type:** Offline learning platform with teacher dashboard
- **Key features:**
  - Lesson creation and assignment to classes/groups
  - Custom quiz builder (question selection, randomization, sections)
  - Per-learner progress tracking (completion %, time spent, quiz scores)
  - Class-wide analytics (who is struggling)
  - Offline content: resources downloaded once, used offline indefinitely
  - Multi-user learner profiles (learners log in with PIN or simple ID)
  - Progress syncs when internet is available
- **Teacher workflow:** Create quiz → assign to group → monitor progress dashboard → adjust grouping
- **Deployment:** Tested in South Asia (Pakistan, India)
- **Status:** Actively maintained, v0.15+ with take-home learning focus

**Source:** https://learningequality-kolibri.mintlify.app/features/coach; https://www.learningequality.org/kolibri/about-kolibri/

### B. Classroom Instruction & Grouping Models

#### **Pratham "Teaching at the Right Level" (TaRL)**
- **Model:** One-time reading level assessment → group by proficiency → teach to level
- **Assessment tool:** One-on-one oral reading check (5 minutes per child)
- **Proficiency levels:** 5-level framework (e.g., letter recognition → fluent reading)
- **Daily structure:** CAMaL (Combined Activities for Maximized Learning)
  - Whole group: shared instruction (songs, phoneme awareness)
  - Small group: guided reading (teacher-led, 3–5 children at same level)
  - Individual: practice and extension
- **Regrouping:** Every 4–6 weeks based on progress assessment
- **Evidence base:** 20+ countries; RCTs show +0.2–0.4 SD gains in 1–2 years
- **Teacher burden:** Requires regular assessment rotation (one new child per lesson = manageable in 40 min)

**Source:** https://prathaminternational.org/teaching-at-the-right-level/; https://www.povertyactionlab.org/case-study/teaching-right-level-improve-learning

#### **Lesson Structure: "I Do, We Do, You Do" (Gradual Release of Responsibility)**
- **Phase 1 (I Do – Teacher Modeling):** Teacher demonstrates phoneme, sound, or decoding strategy aloud
- **Phase 2 (We Do – Guided Practice):** Children echo, read chorally, or do collaborative decoding with teacher support
- **Phase 3 (You Do – Independent Practice):** Children read or decode alone; teacher circulates and provides corrective feedback
- **Duration:** 40-minute lesson might allocate 10 min (I Do) + 15 min (We Do) + 15 min (You Do)
- **Application:** Works for both whole-class and small-group instruction
- **Evidence:** Correlated with improved fluency and comprehension outcomes

**Source:** https://www.formative.com/read/i-do-we-do-you-do; https://thefirstgraderoundup.com/planning-small-group-lesson-thats/

### C. Scripted Lesson Plans & Teacher Guides

#### **Pakistan Reading Project (USAID-funded)**
- **Scope:** Grade 1–2 Urdu, Sindhi, Pashto, Balochi, Brahui
- **Structure:** 100+ scripted lesson plans per language
- **Components:**
  - Explicit phoneme/grapheme teaching (letter sounds)
  - Sound sequencing (which sounds in which order)
  - Blending and decoding activities
  - Fluency practice (timed repeated reading)
  - Comprehension questions
- **Teacher note:** Fully scripted (what to say, when to pause)
- **Duration:** Designed for 40–45 min lessons
- **Availability:** Online at pakreading.org.pk (downloadable PDFs)
- **Evidence:** Evaluated by MSI; published results on learning gains in 7 Pakistani regions

**Source:** https://pakreading.org.pk/; https://pubhtml5.com/wyyh/ozuh/basic/ (Urdu lesson sample)

#### **Room to Read Teacher Guides**
- **Scope:** Early-grade reading instruction in low-income countries
- **Key elements:**
  - Phoneme isolation and blending (simple for teachers)
  - Decodable text at each level
  - Guided reading protocol (pre-reading, during, post-reading questions)
  - Parent engagement (home reading letter, level-appropriate books)
- **Accessibility:** Designed for non-specialist teachers
- **Distribution:** PDF guides + printed student books

**Source:** https://www.teachertaskforce.org/trc-teaching-resource/teachers-guide-early-grade-reading-instruction; https://www.roomtoread.org/literacy-gender-equality/literacy/teacher-training/

### D. Reading Fluency Benchmarks for Pakistan

#### **ASER (Annual Status of Education Report) Pakistan**
- **Target:** Grade 2 and Grade 3 reading fluency in Urdu
- **Benchmark (Grade 3 Urdu):** 60 correct words per minute (cwpm)
- **Benchmark (Grade 2 end):** 45–60 cwpm (fluency threshold for grade-level reading)
- **Grade 2 Grade-Level Text:** 59–63 words (used for 60-second fluency check)
- **Assessment method:** Child reads passage aloud; assessor marks errors; score = correct words in 1 minute
- **Status distribution:** ~50% of Grade 3 students in Pakistan cannot read Grade 2 text fluently (as of 2022)

**Source:** https://img.asercentre.org/docs/Aser+survey/Tools+validating_the_aser_testing_tools__oct_2012__3.pdf; Learning at Scale report (Cost Analysis, Aug 2023)

---

## 3. EGRA Assessment Toolkit: Detailed Flow Specification

### 3.1 EGRA Subtasks (Complete List)

| Subtask | Timing | Scoring Metric | Stop Rule | Notes |
|---------|--------|---|---|---|
| **Concepts of Print** | No time limit | Count correct / total (%) | None | Answering 3–5 yes/no or multiple-choice Q about how a book works |
| **Letter Name Knowledge** | 60 seconds | Correct letters per minute (clpm) | If 0 correct in first 10 items, discontinue | Show flash cards or lines of letters; child names each |
| **Letter Sound Knowledge** | 60 seconds | Correct letter sounds per minute (clspm) | If 0 correct in first 10 items, discontinue | Child says sound for each letter (not name) |
| **Initial Sound Identification** | 2–4 minutes | Correct / total or % | None | Assessor says word aloud; child names first sound (e.g., "cat" → "cuh") |
| **Syllable Counting** | No time limit | Correct / total (%) | None | Child claps or counts syllables in spoken word |
| **Familiar Word Reading** | 60 seconds | Correct words per minute (cwpm) | If 0 correct in first 10 items, discontinue | Child reads grade-level sight words from list |
| **Nonword Decoding** | 60 seconds | Correct nonwords per minute (cnwpm) | If 0 correct in first 10 items, discontinue | Child sounds out invented words (tests decoding ability) |
| **Oral Passage Reading Fluency** | 60 seconds | Correct words per minute (cwpm); also % accuracy | None | Child reads age-grade passage aloud; assessor marks errors |
| **Reading Comprehension** | No time limit | Correct / 5 (1 point each) | None | Assessor asks 5 recall/inference questions on passage |
| **Listening Comprehension** | No time limit | Correct / total | None | Assessor reads passage aloud; child answers questions (tests oral language, not decoding) |

### 3.2 EGRA-on-Tablet Workflow (Teacher Perspective)

**Pre-Assessment Setup**
1. Teacher opens app on tablet
2. Selects "New Assessment"
3. Searches/taps child's name (pre-loaded from class roster or added as new)
4. Confirms child's grade level (auto-selects appropriate passage/item set)

**Assessment Administration** (one child, ~8 minutes)
1. **Concepts of Print** [1 min]:
   - App displays questions one at a time
   - Teacher reads aloud; child answers verbally
   - Teacher taps correct/incorrect
   - Auto-advances after each response

2. **Letter Name & Sound** [2 min total]:
   - App displays letters on screen (if no projector: hold tablet for child to see, or print list)
   - Built-in timer starts when teacher taps "start"
   - Timer counts down from 60 sec (large display)
   - Teacher taps each correct response; taps "error" if child makes mistake or no response
   - **STOP** when 60 sec timer reaches zero (app alerts audibly and visually)
   - App auto-scores: count of correct responses = **clpm** or **clspm**

3. **Familiar Words** [1 min]:
   - Same flow as Letter Names
   - Words appear on screen (or printed sheet)
   - Timer 60 sec
   - Auto-score: **cwpm**

4. **Nonwords** [1 min]:
   - Same as Familiar Words
   - Auto-score: **cnwpm**

5. **Oral Reading Fluency** [2 min]:
   - App displays passage (or teacher holds tablet/printed sheet for child to read)
   - Teacher taps "start" → timer begins (60 sec)
   - Child reads aloud; teacher marks errors as they occur (taps error button each time)
   - At 60 sec, app stops and alerts
   - **Auto-score:** cwpm = (total words read – errors) / 1 minute
   - **Accuracy %** also calculated

6. **Reading Comprehension** [1 min]:
   - App displays 5 questions one at a time
   - Child answers verbally
   - Teacher taps correct/incorrect for each
   - Auto-score: X/5

**Post-Assessment**
- App displays summary for this child:
  - All subtask scores (clpm, cwpm, cnwpm, comprehension, etc.)
  - Pass/Fail by subtask (vs. age-grade benchmarks)
  - Recommended level: below grade level / at grade level / above grade level
- Teacher taps "Save" → data stored on tablet
- App offers option: "Assess another child?" → back to child selection

### 3.3 Class-Level Reporting (Post-Assessment Block)

After assessing all children in a class or group (e.g., 30 children in 4 hours):

**Dashboard View** (available offline)
- **Class summary table:**
  - Child name | Fluency (cwpm) | Comprehension (X/5) | Level | Date
  - Sortable by: fluency (low→high), level, name
- **Distribution chart (optional):**
  - Histogram: # children at each fluency level (below / at / above grade)
- **Action items:**
  - Children below grade level (highlighted in red)
  - Suggested small-group assignments based on level

**Reporting outputs** (generated offline, synced when internet available)
- PDF or CSV export for school admin
- Parent slip (one-page report for each child's caregiver)

---

## 4. Shared-Device Profile Model

### 4.1 Device Setup (One-Time)

**On first app launch:**
1. App asks: "Is this a school tablet (multiple learners) or personal device?"
2. If **school tablet:**
   - Create **Teacher Profile**
     - Input: Teacher name (text), PIN (4–6 digits, numeric only)
     - Stores: All assessment data, class roster, lesson plans, reports
   - Create or upload **Class Roster**
     - Method 1: Enter child names manually (+ grade, age)
     - Method 2: CSV import (name, grade, age, ID number)
   - **Data isolation:** Only this teacher's data visible when logged in with this PIN
   - Teacher PIN is required to:
     - Modify roster
     - Create/edit lessons
     - View reports
     - Change settings

3. If **personal device:**
   - Single parent/tutor profile
   - No PIN (or optional PIN for app access)

### 4.2 Learner Profile Switching (Daily Use)

**For multiple learners on a shared tablet:**

**Entry point:** Home screen shows list of children in class
- Tap child's name → load that child's profile
- If child is new, tap "Add Child" → enter name/grade → confirm

**Per-child data stored:**
- All assessments (EGRA, quiz scores, fluency checks)
- Lessons completed / in progress
- Current reading level (inferred from latest EGRA)
- Progress graph (fluency over time)
- Parent notes or teacher comments

**Switching between learners:**
- Tap "Back to Class" or child list icon
- Tap different child name
- New child's data loads (instant, offline)
- No login required (teacher already authenticated once)

### 4.3 Offline Syncing & Multi-Device Scenarios

**Scenario 1: Single tablet, no internet**
- All data stored locally
- No backup
- **Risk:** Loss if device breaks
- **Mitigation:** Export weekly to USB drive (if one laptop available)

**Scenario 2: Multiple tablets, periodic school internet**
- Each tablet has same teacher PIN
- When internet available (e.g., school office):
  - Teacher taps "Sync Data"
  - App uploads all local assessments/lessons to cloud server (encrypted)
  - Downloads latest class roster, lesson updates, curriculum
  - Offline copy remains on tablet
- **Conflict resolution:** If same child assessed on two tablets:
  - Server keeps both records (timestamped)
  - Teacher sees: "Assessment from Tablet 1 (Sept 15, 2pm) vs. Tablet 2 (Sept 15, 4pm)"
  - Teacher marks newer one as "official"

**Scenario 3: Parent/home tutor with personal device**
- Single learner profile (child's progress)
- Optional parent login (email + password) to backup progress to cloud
- Export child's report as PDF to email to teacher

---

## 5. Teacher Mode: Feature List (Must-Have vs. Nice-to-Have)

### Must-Have Features (Classroom Mode)

| Feature | Source/Justification | Implementation Notes |
|---------|---|---|
| **EGRA Assessment (All 9 subtasks)** | Tangerine, EGRA toolkit, ASER Pakistan | Built-in timer, auto-scoring, tap-based marking |
| **Class Roster & Child Profiles** | Kolibri, Tangerine | CSV import, manual entry, grade + age fields |
| **Teacher PIN login** | Kolibri, low-resource context | No email required; 4–6 digit PIN unlocks all teacher features |
| **Assessment Results Storage** | Tangerine, Kolibri | Offline local storage; sync when internet available |
| **Reading Level Inference** | ASER, TaRL, Tangerine | Auto-assign level (below/at/above grade) based on fluency + comprehension |
| **Learner Grouping by Level** | Pratham TaRL | Visual grouping view: sort/filter children by level; suggest small groups for rotation |
| **Class Summary Report** | Tangerine, Kolibri Coach | Table view (child name, fluency cwpm, comprehension score, level) |
| **Fluency Benchmark Overlay** | ASER Pakistan benchmarks | Display target (60 cwpm Grade 3 Urdu, 45 cwpm Grade 2) alongside actual scores |
| **Quiz/Quick Check Tool** | Kolibri Coach | Create simple quiz (5–10 questions); assign to group; auto-score; track completion |
| **Lesson Lesson Template Library** | Pakistan PRP, Room to Read | Structured templates: "I do, we do, you do" sections + scripted talking points |
| **Offline Operation** | Tangerine, Kolibri | All core features work 100% offline; no internet required |
| **Quick Learner Profile Switch** | Kolibri | Tap child name → instant load (no logout/login cycle) |
| **Parent Report Export** | ASER, Tangerine | One-page PDF per child: fluency, level, next steps (printable) |

### Nice-to-Have Features (Classroom Mode)

| Feature | Source/Justification | Notes |
|---------|---|---|
| **Progress Graphs Over Time** | Kolibri Coach | Fluency trajectory (cwpm by date) for individual or class |
| **Home Reading Assignments** | Room to Read, Taleemabad | Suggest passage at child's level; parent/tutor confirms completion |
| **Phoneme Sequencing Guide** | Pakistan PRP, Room to Read | Pop-up or reference card: order to teach sounds (e.g., m, a, t, s, in → mat, is, sit) |
| **Automated Grouping Suggestions** | TaRL, Kolibri Coach | "Regroup every 4 weeks" reminder + auto-suggestions based on latest fluency |
| **Speech Recognition for Fluency** | Tangerine (research phase) | AI listens while child reads; flags errors automatically (reduces teacher marking load) |
| **Teacher Notes / Observations** | Taleemabad, Kolibri | Free-text field per assessment: "Child was sick," "Made rapid progress," etc. |
| **SMS Alerts for Below-Level Children** | Low-resource context need | Send SMS to parent when child falls below fluency threshold |
| **Offline Sync Queue** | Tangerine, Kolibri | Show pending uploads; let teacher control when to sync (to preserve data bandwidth) |
| **Comparative Benchmarking** | ASER Pakistan | Compare class fluency to provincial/national average (if user opts in) |
| **Curriculum Sequencing** | Pakistan PRP, Pratham | Lock/unlock lessons based on child's level; prevent skipping prerequisites |

### Nice-to-Have Features (Home Tutor Mode)

| Feature | Source/Justification | Notes |
|---------|---|---|
| **Parent Phonics Guide** | Jolly Phonics (parent support resources), Kids Bolo | Illustrated guide: how to teach each sound, what to listen for |
| **Pronunciation Feedback** | Speech recognition tech (proprietary) | Record child reading; app shows which phonemes are clear vs. unclear |
| **Motivational Progress Badges** | Gamification, heritage language app design | Stars, certificates, level badges when child reaches fluency goals |
| **Mother-Child Paired Reading** | Home reading research | Suggested turn-taking reading activity (adult reads sentence, child echoes) |
| **Heritage Language Tips** | Heritage learner contexts | Culturally responsive: celebrate Urdu literature, poets, cultural holidays |
| **Parent Chat with Teacher** | Modern LMS pattern | Secure message: parent asks teacher about child's progress (optional, teacher may disable) |

---

## 6. Integration with Larger App Ecosystem

### Connection Points with Learner Mode

**Learner-Facing Features** → **Teacher-Facing Data**
- Child completes quiz in Learner mode
  - Quiz results auto-sync to Teacher mode
  - Teacher sees completion % + score without reopening child's profile
- Child practices fluency (reads passage in Learn mode)
  - If speech recognition enabled: flagged words → appears in Teacher's "needs help" list
- Teacher assigns home reading in Teacher mode
  - Child sees assigned book in Learn mode (marked as "homework")
  - Child completes → "done" marked in Teacher mode

### Curriculum Sequencing (Optional)

**If app includes lesson content:**
- Teacher mode locks lessons by level (e.g., "Lesson 3 requires ≥45 cwpm")
- Child cannot access Lesson 3 until assessment shows ≥45 cwpm
- Prevents frustration from skipping prerequisites

---

## 7. Sources & Reference Links

### Assessment & Benchmarking Tools

1. **Tangerine (EGRA-on-Tablet):**
   - Site: https://www.tangerinecentral.org/
   - RTI product page: https://www.rti.org/impact/tangerine-mobile-reading-mathematics-assessments
   - GitHub (open-source): https://github.com/Tangerine-Community/Tangerine
   - Use case: 5M+ assessments, 65+ countries

2. **EGRA Subtasks & Toolkit:**
   - Early Grade Reading Barometer: https://www.earlygradereadingbarometer.org/resources/subtasks
   - EGRA Toolkit PDF (V2, 2016): https://ierc-publicfiles.s3.amazonaws.com/public/resources/EGRA+Toolkit+V2+2016.pdf
   - Validation study (ASER tools vs. EGRA): https://img.asercentre.org/docs/Aser+survey/Tools+validating_the_aser_testing_tools__oct_2012__3.pdf

3. **ASER Pakistan Reading Benchmarks:**
   - Annual Status of Education Report Pakistan: https://www.asercentre.org/ (Pakistan page)
   - Learning at Scale cost analysis (2023): https://learningatscale.net/ (report includes Urdu 60 cwpm benchmark)
   - Urdu benchmark: **60 cwpm at end of Grade 3**; **45–60 cwpm fluency threshold for Grade 2**

### Classroom Instruction Models

4. **Pratham "Teaching at the Right Level" (TaRL):**
   - https://prathaminternational.org/teaching-at-the-right-level/
   - https://www.povertyactionlab.org/case-study/teaching-right-level-improve-learning
   - CAMaL framework reference: daily structured activities (whole class + small group + individual)

5. **Gradual Release of Responsibility ("I Do, We Do, You Do"):**
   - Formative explanation: https://www.formative.com/read/i-do-we-do-you-do
   - The First Grade Roundup lesson planning: https://thefirstgraderoundup.com/planning-small-group-lesson-thats/

6. **Small-Group Reading Instruction (K–5):**
   - Reading Rockets: https://www.readingrockets.org/classroom/instructional-routines-and-grouping/k-5-small-group

### Curriculum & Scripted Lessons

7. **Pakistan Reading Project (USAID):**
   - Main site: https://pakreading.org.pk/
   - Resources page: https://pakreading.org.pk/resources/publications/reading-learning-material
   - Urdu lesson sample: https://pubhtml5.com/wyyh/ozuh/basic/
   - **Status:** UNVERIFIED in terms of current availability/maintenance (site exists but last update date unclear)

8. **Room to Read Teacher Guides:**
   - Organization site: https://www.roomtoread.org/literacy-gender-equality/literacy/teacher-training/
   - Teacher's guide (full PDF): https://www.teachertaskforce.org/trc-teaching-resource/teachers-guide-early-grade-reading-instruction
   - Methodology: phonics, decodable books, guided reading, parent engagement

### Offline Learning Platforms

9. **Kolibri Coach (Learning Equality):**
   - Main site: https://www.learningequality.org/kolibri/about-kolibri/
   - Coach documentation: https://learningequality-kolibri.mintlify.app/features/coach
   - GitHub: https://github.com/learningequality/kolibri
   - Deployment note: Tested in Pakistan/India low-resource contexts; multi-user profiles, offline quiz creation

10. **HundrED overview (Kolibri):** https://hundred.org/en/innovations/kolibri

### Urdu/Heritage Language Learning Tools

11. **Hikmat.AI (Urdu-specific lesson generation):**
    - Reference: https://www.linkedin.com/posts/pakistanmagazineofficial_edtech-hikmatai-urdueducation-activity-7355979174718664704-gJ0v
    - **Status:** UNVERIFIED (tool existence confirmed; detailed features unclear)
    - Focus: AI-generated lesson content for Urdu teachers

12. **NABU (Multilingual children's books app):**
    - Site: https://www.nabubooks.org/ (inferred from F6S listing)
    - **Status:** UNVERIFIED (focus: bilingual books, not assessment)

13. **Kids Bolo (Urdu learning platform):**
    - Reference in heritage language context: https://aaww.org/tlp-learning-urdu-the-pakistani-canadian-way/
    - **Status:** UNVERIFIED in terms of teacher tools (appears to be learner-facing)

### Context & Low-Resource Classroom Challenges

14. **"Offline and Low-Data AI Tools for Schools in Pakistan":**
    - https://www.edugenius.app/blog/offline-and-low-data-ai-tools-for-schools-in-pakistan
    - Key insight: "One Android box or Kolibri server per classroom, projected or shared across small groups"

15. **Mother Tongue Based Multilingual Education (Pakistan):**
    - TCF Pakistan model: https://www.tcf.org.pk/mother-tongue-based-multilingual-education/
    - Thar Foundation partnership (Tharparkar): language-specific instruction from Dhatki/Sindhi to Sindhi regional

---

## 8. Design Recommendations for Teacher Mode

### Priority 1: MVP (Minimum Viable Product)

**Build first (8–12 weeks):**
1. EGRA assessment (all 9 subtasks, built-in timer, tap-marking)
2. Class roster + child profiles
3. Teacher PIN login (no email)
4. Assessment results storage (offline) + simple class table report
5. Reading level inference (vs. Pakistan benchmarks)
6. Learner grouping view (sort by level)
7. Parent report export (PDF)

### Priority 2: Classroom Expansion (12–20 weeks)

**Add once MVP is tested:**
1. Quiz/quick check tool (create + assign + auto-score)
2. Lesson template library ("I do, we do, you do" structure)
3. Offline syncing when internet available
4. Progress graphs over time

### Priority 3: Home Tutor Support (20–32 weeks)

**Launch as separate mode or feature gate:**
1. Parent/home tutor profile type
2. Phoneme teaching guide (illustrated)
3. Motivational badges
4. Parent chat (optional, optional disable by teacher)

### UX Principles for Low-Resource Context

- **No email logins:** PIN or child name only
- **Tap, not type:** Multiple-choice options, autocomplete, tap buttons (not text entry)
- **Offline-first:** All features work without internet; syncing is optional
- **Simple colors:** High contrast (black text on white background) for tablet readability in sunlight
- **Large fonts:** 18pt+ for timer, child names, button labels
- **Minimal scrolling:** Fit critical info on one screen where possible
- **Clear icons:** Use universal symbols (plus = add, trash = delete, checkmark = correct)
- **Audible alerts:** Timer beep when 60 sec is up (helpful in noisy classroom)

### Assessment Accuracy Safeguards

- **Assessor training:** In-app tutorial (3–5 min video) showing how to mark each subtask correctly
- **Early stop rule enforcement:** App enforces stopping rules (e.g., "0 correct in first 10 items")
- **Double-check prompts:** Before saving assessment, show summary and ask "Is this correct?"
- **Comment field:** Allow assessor to note if child was unwell, distracted, etc. (for context)

---

## 9. Unknowns & Gaps (Marked UNVERIFIED)

| Item | Status | Notes |
|------|--------|-------|
| Pakistan Reading Project lesson availability | UNVERIFIED | Website exists but current maintenance/download status unclear |
| Hikmat.AI features & pricing | UNVERIFIED | Tool confirmed to exist; specific features (teacher UX, offline capability) not documented |
| Kids Bolo teacher dashboard | UNVERIFIED | Known as heritage learner app; teacher-facing features not confirmed |
| NABU app teacher role | UNVERIFIED | Confirmed as multilingual books app; no teacher/classroom data features documented |
| Kolibri offline quiz creation | UNVERIFIED | Documentation mentions "custom quiz" but unclear if this works fully offline or requires server |
| Speech recognition accuracy for Urdu | UNVERIFIED | Tangerine mentions non-cognitive assessment research; no published Urdu speech model accuracy data |
| Whether 40-min lesson can fit full EGRA + instruction | UNVERIFIED | Practical data: one EGRA assessment takes ~8 min; if assessing 30 children with one tablet, that's 4 hours total. Feasibility depends on whether all 30 are assessed in one block (before instruction) or assessment happens during station rotation. |

---

## 10. Next Steps for App Development

1. **Validate EGRA subtask flow with real assessor:** Spend one day in Pakistan classroom; observe one trained assessor administer EGRA on paper; confirm tablets can replicate workflow.

2. **Test Tangerine source code:** Fork Tangerine GitHub; extract EGRA subtask modules; evaluate code quality and feasibility of customizing for Urdu.

3. **Interview 3–5 Punjab/KP teachers:** What is their typical 40-minute lesson? How do they currently group children? What assessment tools do they have (if any)?

4. **Benchmark offline syncing library:** Evaluate Firebase Offline Persistence vs. local SQLite vs. custom sync engine; test sync speed on low-bandwidth connection.

5. **Prototype parent report PDF generation:** Design one-page template; test PDF rendering on low-end Android devices.

6. **Conduct feasibility study:** Can one teacher realistically administer EGRA to 30 children + teach 3 small groups in a 40-minute block? If not, what is realistic workflow?

---

**Document compiled:** 2026-09-18  
**Confidence level:** Moderate (core tools verified; Pakistan-specific benchmarks confirmed; some third-party tools marked UNVERIFIED due to limited public documentation)
