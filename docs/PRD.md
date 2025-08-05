# Product Requirements Document (PRD)

## 1. Overview
This document outlines the requirements and vision for the Interview Simulation Platform, as generated via the Project Genesis workflow (Session 5).

## 2. Product Vision
A robust, fully async, role-based interview simulation platform for candidates and interviewers, leveraging LLMs (OpenAI gpt-4o-mini) and Google Cloud TTS for question delivery, with automated scoring and eligibility feedback.

## 3. Key Features
- Django backend with Django templates for frontend (no UI libraries)
- Django authentication and role-based access (candidate, interviewer, admin)
- Integration with OpenAI (gpt-4o-mini) for question generation and scoring
- Google Cloud TTS for all question audio
- Candidates can have multiple, time-bound interview sessions
- Automated scoring/feedback (overall score, eligibility %)
- Long-term storage of candidate responses
- Fully async interview flow
- Handles network interruptions gracefully
- No GDPR or strict SLAs required

## 4. User Stories
- As a candidate, I can register, log in, and take interviews with audio questions and automated feedback.
- As an interviewer, I can create/manage question sets and review candidate performance.
- As an admin, I can manage users, roles, and monitor system health.

## 5. Non-Functional Requirements
- Secure authentication and data storage
- Scalable to support multiple concurrent interviews
- Resilient to network interruptions
- No fallback to non-OpenAI LLMs
- No strict block diagram tool or UI library requirements

## 6. Out of Scope
- GDPR compliance
- Strict SLAs
- Use of UI libraries or block diagram tools

---

*This PRD was generated based on the clarified requirements and Project Genesis workflow (Session 5).*
