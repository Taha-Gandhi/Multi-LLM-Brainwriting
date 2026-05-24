# Multi-LLM Brainwriting Platform

A research prototype for comparing human and LLM-based convergence in group brainwriting.

This project extends AI-augmented brainwriting by exploring how different forms of discussion and convergence affect the quality of final ideas. The platform supports human-only brainwriting sessions and LLM-based debate workflows.

The main goal of this project is to study how people and AI systems generate, discuss, select, and refine ideas during a creative ideation task.

---

## Project Overview

Traditional brainstorming can sometimes be affected by social pressure, dominant voices, unequal participation, and production blocking. Brainwriting helps reduce these issues by letting participants first write ideas independently before discussing them as a group.

This project extends that idea by comparing different ways of moving from individual ideas to a final selected idea.

The project has four study conditions:

1. **1a — Anonymous Human Convergence**
2. **1b — Open Human Convergence**
3. **2a — Human Ideas with LLM Convergence**
4. **2b — LLM Ideas with LLM Convergence**

The current web platform mainly supports the two human conditions:

- **1a: Anonymous Human Convergence**
- **1b: Open / Non-anonymous Human Convergence**

Both conditions use the same interface structure, but the way participant identity is displayed changes depending on the condition.

---

## Research Conditions

### 1a — Anonymous Human Convergence

In this condition, participants join a shared brainwriting room and contribute ideas anonymously.

Participants can:

- Submit exactly one idea
- Delete their own idea and submit a new one if needed
- Discuss ideas in idea-specific comment threads
- Use the general group chat
- Vote for one idea at a time
- Remove or change their vote
- Work together to write one final collaborative idea

Participant names and student IDs are collected for researcher tracking, but they are hidden from other participants inside the interface.

Example anonymous labels:

```text
Anonymous Participant
Anon 3
Anon 7
```

This condition is used to study whether anonymity changes discussion behavior, participation, and convergence quality.

---

### 1b — Open Human Convergence

In this condition, the interface is almost the same as 1a, but participant names are visible.

Participants can:

- Submit exactly one named idea
- Delete their own idea and submit a new one if needed
- Comment with their name visible
- Chat with their name visible
- Vote for one idea at a time
- Remove or change their vote
- Work together to write one final collaborative idea

Example open labels:

```text
Submitted by Anjali
Anjali commented
Anjali sent a chat message
```

This condition is used to compare anonymous and non-anonymous discussion behavior.

---

### 2a — Human Ideas with LLM Convergence

In this condition, human-generated ideas can be passed into a multi-LLM agent system.

The LLM agents can:

- Read human ideas
- Discuss strengths and weaknesses
- Debate possible improvements
- Refine or merge ideas
- Vote or select a final direction

This condition helps study whether LLMs can support convergence after humans provide the initial creative input.

---

### 2b — LLM Ideas with LLM Convergence

In this condition, LLM agents generate ideas and then debate with each other to select or refine a final idea.

The agents can be given different roles or personalities, such as:

- Creative agent
- Practical agent
- Critical agent
- Balanced agent

This condition helps study whether LLM-only ideation and convergence can produce useful final ideas without human input.

---

## Current Web Platform

The current deployed web app supports the human study conditions:

```text
1a: Anonymous Human Convergence
1b: Open Human Convergence
```

The same website can be used for both conditions by changing the URL parameters.

Example anonymous condition link:

```text
https://multi-llm-brainwriting.vercel.app/?session=group-1a-a&condition=1a
```

Example open condition link:

```text
https://multi-llm-brainwriting.vercel.app/?session=group-1b-a&condition=1b
```

---

## Main Features

### 1. Session-Based Study Rooms

Each study group can have its own session link.

Example sessions:

```text
pilot
group-1a-a
group-1a-b
group-1b-a
group-1b-b
```

All ideas, comments, chat messages, votes, participant access records, and final ideas are stored separately for each session.

This prevents data from different groups from mixing.

---

### 2. Participant Access Form

Before entering the study room, each participant must fill in:

- Full name
- Student ID
- Session password

After submitting the form, the participant does not immediately enter the study room. Their request is saved in Firebase with:

```text
approved: false
```

The researcher can approve the participant manually in Firebase by changing:

```text
approved: false
```

to:

```text
approved: true
```

Once approved, the participant can refresh the page and enter the study room.

This allows the researcher to control who enters each session.

---

### 3. Session-Specific Passwords

Each session has its own access password.

Example:

```text
Session: pilot
Password: PILOT1A

Session: group-1a-a
Password: GROUPA1A

Session: group-1b-a
Password: GROUPA1B
```

This makes it easier to run separate study groups without mixing participants.

---

### 4. Anonymous and Open Modes

The interface automatically changes depending on the `condition` value in the URL.

Anonymous mode:

```text
?condition=1a
```

Open mode:

```text
?condition=1b
```

This allows one codebase to support both study conditions.

---

### 5. Study Flow Section

The interface includes a simple study flow to guide participants:

1. Submit exactly one idea
2. Comment under specific idea threads
3. Use the group chat to compare ideas
4. Vote for one idea, but not your own
5. Write the final collaborative idea

This helps participants understand what they are expected to do during the session.

---

### 6. Before You Start Rules

The platform includes a participant-facing rules panel.

The rules explain that participants should:

- Submit exactly one idea
- Not use AI for their initial idea
- Read other ideas before voting
- Comment constructively
- Vote for only one idea at a time
- Avoid voting for their own idea
- Use the group chat to converge on one final direction
- Keep the final collaborative idea short and clear

This keeps the session structured and easy to follow.

---

### 7. Exactly One Idea Per Participant

Each participant can submit only one idea per session.

After submitting an idea, the submit button becomes disabled.

However, participants can delete their own idea if they want to replace it.

This means they can:

```text
Submit idea
Delete own idea
Submit a new idea
```

They cannot delete other participants' ideas.

This keeps the study controlled while still allowing small corrections.

---

### 8. Idea Board

All submitted ideas appear in the idea board.

Each idea card shows:

- Idea number
- Idea title
- Idea description
- Vote count
- Author display label

In anonymous mode, the idea shows:

```text
Submitted anonymously
```

In open mode, the idea shows:

```text
Submitted by [participant name]
```

Participants can click an idea card to open its detailed discussion thread.

---

### 9. Thread Discussion

Each idea has its own discussion thread.

Participants can comment under a specific idea to:

- Ask questions
- Suggest improvements
- Critique the idea
- Combine it with other ideas
- Clarify implementation details

In anonymous mode, comments appear anonymously.

In open mode, comments appear with participant names.

This supports focused discussion around each individual idea.

---

### 10. General Group Chat

The platform includes a general group chat.

This chat is used for broader discussion, such as:

- Comparing ideas
- Discussing patterns
- Negotiating final direction
- Deciding which ideas should be merged
- Agreeing on one final collaborative idea

In anonymous mode, chat messages hide participant names.

In open mode, chat messages show names.

---

### 11. Voting System

The voting system is participant-based.

Each participant can vote for only one idea at a time.

Participants can:

- Vote for an idea
- Remove their vote
- Change their vote to another idea

Participants cannot:

- Vote for their own idea
- Vote for multiple ideas at the same time

This makes the voting process fairer and cleaner for analysis.

---

### 12. Final Collaborative Idea

At the end of the discussion, the group writes one final collaborative idea.

The final section includes:

- Final idea title
- Final idea description

The final idea should be short, clear, and understandable for someone who did not participate in the session.

This final idea can later be used for evaluation and comparison with outputs from other conditions.

---

### 13. Firebase Data Storage

The platform uses Firebase Firestore to store live session data.

Each session stores:

```text
sessions
  sessionId
    participants
    ideas
    generalChat
    sessionData
      finalIdea
```

This includes:

- Participant access records
- Submitted ideas
- Idea comments
- Vote records
- General chat messages
- Final collaborative idea

Because the data is stored in Firebase, multiple participants can interact with the study room live.

---

### 14. JSON Export

The platform includes an export button that downloads the session data as a JSON file.

The exported data includes:

- Session condition
- Session ID
- Design challenge
- Ideas
- Comments
- Votes
- General chat messages
- Final collaborative idea

This is useful for later analysis.

---

## Interface Walkthrough

### Access Page

The participant first sees a restricted access page.

They must enter:

```text
Full name
Student ID
Password
```

After submitting, they wait for researcher approval.

---

### Waiting for Approval Page

After a valid access request, the participant sees a waiting screen.

The page tells them that their request has been submitted and that they should wait for the researcher to approve their access.

Once the researcher approves them in Firebase, they can refresh the page and enter the study room.

---

### Hero Section

The top of the study room shows the current condition.

For example:

```text
1a Anonymous Human Convergence
```

or:

```text
1b Open Human Convergence
```

It also briefly explains what participants should do in the session.

---

### Design Challenge Section

The design challenge explains the main problem participants are solving.

Current challenge:

```text
Design a solution that improves creative collaboration and idea selection in group brainwriting.
```

Participants use this challenge as the basis for their idea generation and discussion.

---

### Mode Banner

The mode banner clearly tells participants whether they are in anonymous mode or open mode.

In anonymous mode, it explains that their identity is hidden from other participants.

In open mode, it explains that their name is visible with their ideas, comments, and chat messages.

---

### Study Flow

The study flow gives participants a simple step-by-step process:

```text
Submit → Thread → Discuss → Vote → Converge
```

This makes the interface easier to understand.

---

### Rules Panel

The rules panel explains the main study rules before participants begin.

It reminds them to submit exactly one original idea and to vote fairly.

---

### Idea Submission Panel

Participants use this panel to submit their idea.

They enter:

```text
Idea title
Idea description
```

After submitting one idea, they cannot submit another unless they delete their own idea first.

---

### Idea Board

The idea board shows all submitted ideas in the session.

Participants can click any idea to open its detailed discussion thread.

---

### Idea Detail and Thread Panel

This panel shows the selected idea in detail.

Participants can:

- Read the idea
- Vote for the idea
- Remove or change their vote
- Comment in the idea-specific thread
- Delete their own idea if needed

---

### General Chat Panel

The general chat allows the group to discuss the overall direction of the session.

This is useful for convergence because participants can compare ideas and decide what should become the final collaborative idea.

---

### Final Collaborative Idea Panel

This is where the group writes the final idea.

The final idea should summarize the best outcome of the session.

It includes:

```text
Final idea title
Final idea description
```

---

## Technology Stack

### Frontend

```text
React
Vite
CSS
Lucide React Icons
```

### Backend / Database

```text
Firebase Firestore
```

### Deployment

```text
Vercel
```

---

## Project Structure

A simplified version of the project structure:

```text
Multi-LLM-Brainwriting
  ├── human-condition-webapp
  │   ├── src
  │   │   ├── App.jsx
  │   │   ├── firebase.js
  │   │   ├── index.css
  │   │   └── main.jsx
  │   ├── package.json
  │   └── vite.config.js
  │
  ├── src
  │   ├── agents.py
  │   └── llm_client.py
  │
  ├── run_llm_condition.py
  ├── run_hybrid_condition.py
  └── README.md
```

---

## How to Run the Web App Locally

Go into the human web app folder:

```bash
cd human-condition-webapp
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

Open the local URL shown in the terminal.

Example:

```text
http://localhost:5173/?session=pilot&condition=1a
```

---

## Example Study Links

### Anonymous Human Condition

```text
https://multi-llm-brainwriting.vercel.app/?session=group-1a-a&condition=1a
```

Password:

```text
GROUPA1A
```

---

### Open Human Condition

```text
https://multi-llm-brainwriting.vercel.app/?session=group-1b-a&condition=1b
```

Password:

```text
GROUPA1B
```

---

## Example Session Passwords

```text
pilot           → PILOT1A
test-vote       → TEST1A

group-1a-a      → GROUPA1A
group-1a-b      → GROUPB1A
group-1a-c      → GROUPC1A

group-1b-a      → GROUPA1B
group-1b-b      → GROUPB1B
group-1b-c      → GROUPC1B

default-session → BRAINWRITE1A
```

---

## Research Use

This platform is designed for a Human-Computer Interaction research project.

It can be used to study:

- Whether anonymity changes discussion behavior
- Whether open discussion produces different convergence patterns
- Whether participants engage more equally when anonymous
- How human convergence compares with LLM-based convergence
- How discussion activity relates to final idea quality
- How human and LLM evaluation preferences differ

---

## Data Collected

The system may collect:

- Participant name
- Student ID
- Session ID
- Condition type
- Ideas
- Comments
- Chat messages
- Votes
- Final collaborative idea
- Timestamps

In anonymous mode, participant names are hidden from other participants but still stored for researcher tracking.

---

## Current Status

Completed:

```text
Human condition web platform
Firebase live database connection
Session-based access control
Researcher approval through Firebase
Anonymous mode
Open mode
One idea per participant
Delete and resubmit own idea
One vote per participant
Remove or change vote
Block voting for own idea
Idea-specific threads
General group chat
Final collaborative idea panel
JSON export
Vercel deployment
```

Still to do:

```text
Run full participant study
Collect final outputs from 1a and 1b
Run LLM-based 2a and 2b conditions
Prepare blind evaluation survey
Analyze final idea quality and discussion behavior
Write final report
```

---

## Notes for Researchers

The participant access system is intentionally simple for a research prototype.

Participants request access through the form, and the researcher approves them manually in Firebase.

This allows controlled access without needing a full authentication system.

For a larger deployment, this could later be upgraded with:

- Firebase Authentication
- Admin dashboard
- Role-based access
- Automatic email invitations
- More detailed participant management

---

## License

This project is for academic and research use.
