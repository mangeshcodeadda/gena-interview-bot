# Technical Architecture Document

## 1. System Overview
The Interview Simulation Platform is built on Django, using Django templates for the frontend and integrating with OpenAI (gpt-4o-mini) and Google Cloud Text-to-Speech (TTS) APIs. The platform supports role-based access, async interview flows, and automated scoring/feedback.

## 2. Technology Choices
- **Backend:** Django (Python)
- **Frontend:** Django templates (no JS UI libraries)
- **Authentication:** Django auth with custom roles (candidate, interviewer, admin)
- **LLM Integration:** OpenAI gpt-4o-mini (direct, no fallback)
- **TTS:** Google Cloud TTS for all questions
- **Database:** Default (SQLite for dev, pluggable for prod)
- **Async:** Django async views and task handling
- **Storage:** Long-term storage of responses (DB/filesystem)

## 3. System Design
- **User Roles:**
  - Candidate: Takes interviews, receives feedback
  - Interviewer: Manages questions, reviews results
  - Admin: Manages users, roles, system
- **Interview Flow:**
  - Candidate logs in, selects/interview session
  - Questions delivered via TTS (audio)
  - Answers submitted (typed/audio)
  - LLM scores responses, gives feedback
  - Results stored for review
- **Async Handling:**
  - Interview sessions and scoring are non-blocking
  - Handles network interruptions gracefully
- **Security:**
  - Django auth, session management
  - Role-based permissions

## 4. Integration Points
- **OpenAI API:** For question generation and scoring
- **Google Cloud TTS:** For audio delivery of questions

## 5. Deployment Considerations
- No strict SLAs or GDPR
- Scalable to multiple concurrent users
- No UI libraries or block diagram tools

---

*This document reflects the current technical architecture and design choices for the Interview Simulation Platform.*
