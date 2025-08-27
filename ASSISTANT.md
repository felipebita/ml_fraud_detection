# AI Assistant Onboarding Guide

Welcome, Assistant. This guide is your primary entry point for understanding and contributing to this project. Follow these protocols to ensure our collaboration is smooth and effective.

## 1. Core Directives

These are your foundational rules. Follow them at all times.

*   **Your Role is to Provide Commands:** You **do not** run commands yourself. Your primary role is to provide the correct commands for the user to execute in their terminal.
*   **Primacy of the `Makefile`:** Always provide commands that use `Makefile` targets (e.g., `make test`, `make lint`).
*   **Read Before You Write:** Never assume the contents of a file. Always read a file before proposing changes to it.
*   **Consult the Docs First:** The project documentation is your source of truth. Find answers there before asking the user.

## 2. Onboarding Protocol

Execute this protocol every time you start a new session to gain the necessary context.

### Step 1: Read this Guide
You are reading it now. This is always your first step.

### Step 2: Read the Core Documentation
To understand the project's context, goals, and structure, read these five files in order:

1.  `docs/business.md` (The "Why")
2.  `project_development/PROJECT_PLAN.md` (The "What")
3.  `project_development/LAST_SESSION.md` (The "What's Next")
4.  `docs/usage.md` (The "How")
5.  `docs/project_files.md` (The "Where")

For any other file, wait for me to explicitly ask you to read it.

## 3. Standard Operating Procedures (SOPs)

Follow this simplified procedure for all coding tasks.

### SOP-01: All Code Modifications (Features, Bugs, Refactors)
1.  **Understand the Goal:** Discuss the task with me to ensure you understand the requirements.
2.  **Locate & Read:** Identify the relevant files to the task. Read them to understand the current implementation.
3.  **Propose Code Changes:** Based on your understanding, propose the necessary code modifications. Explain your reasoning clearly.
4.  **Propose Validation Commands:** After providing the code, **always** provide the `make test` and `make lint` commands so I can validate the changes on my end.
