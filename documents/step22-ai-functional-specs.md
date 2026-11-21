# NeatSprint – Step 22: AI Assistant Functional Specifications

This document defines the **Product Experience** and **Business Rules** for the AI Assistant modules. It is powered by the architecture defined in **[Step 21: AI Architecture](step21-ai-architecture.md)**.

---

## 1. Core Capabilities (User Stories)

### 1.1. "NeatSprint Ask" (Project Assistant)
**Intent**: `QUERY_PROJECT`
**User Story**: "As a Developer, I want to ask questions about current tasks so I don't have to search manually."
-   **Prompt**: "What is the status of the Login Flow task?"
-   **System Behavior**:
    1.  Router identifies intent.
    2.  SQL Agent queries `tasks` table for `title ILIKE '%Login Flow%'`.
    3.  Returns specific status, assignee, and comments.

### 1.2. Standup Generator
**Intent**: `GENERATE_SUMMARY`
**User Story**: "As a Team Member, I want a bulleted summary of my work yesterday to post in Slack/Teams."
-   **Prompt**: "Write my standup for yesterday."
-   **System Behavior**:
    1.  Fetches `work_logs` where `user_id = current_user` AND `date = yesterday`.
    2.  Fetches `task_status` changes.
    3.  Summarizes into:
        -   **Yesterday**: Worked on Auth Service (3h), Fixed Bug-102.
        -   **Today**: Continuing Auth Service implementation.
        -   **Blockers**: None.

### 1.3. Risk Analysis (Manager)
**Intent**: `ANALYZE_RISK`
**User Story**: "As a Manager, I want to know if we are on track for the sprint deadline."
-   **Prompt**: "Are we on track for the Q2 Launch?"
-   **System Behavior**:
    1.  Calculates `velocity` vs `remaining_points`.
    2.  If `projected_completion > deadline`, flags **High Risk**.

---

## 2. Interaction Model

### 2.1. Context Awareness
The AI does not "know everything". It is restricted to a specific **Context Window** per request to ensure accuracy and privacy.

| Context Scope | Includes | excluded |
| :--- | :--- | :--- |
| **Global** | Company Name, Current Date. | Other Tenants' Data. |
| **Session** | Current User ID, Role, Active Project ID. | Private DMs of other users. |
| **RAG** | Top-5 vector matches from docs/comments. | Deleted Screenshots. |

### 2.2. Voice Experience
-   **Method**: **Push-to-Talk** (Spacebar hold / Widget tap). *No "Always Listening".*
-   **Transcription**:
    -   **Mobile/Desktop**: Local OS Speech-to-Text (Apple Dictation / Windows Voice Typing).
    -   **Fallback**: Whisper API (OpenAI) if local fails.

---

## 3. Guardrail Specifications (Business Rules)

These rules are hard-coded into the `Router Agent` and `Action Executor`.

### 3.1. The "Authorization Mirror" Rule
> *The AI cannot access any data record that the User cannot access via the standard API.*

-   **Implementation**: The AI Service makes internal API calls using the **User's JWT** (On-Behalf-Of flow).
-   **Effect**: If a Developer asks "What is the Admin budget?", the API returns `403`, and the AI responds: *"I cannot access budget information."*

### 3.2. The "Action Confirmation" Rule
> *The AI can never modify data without explicit user confirmation.*

-   **Workflow**:
    1.  User: "Create a task for the Logo Design."
    2.  AI: "I have drafted a task: **Title**: Logo Design, **Project**: Marketing. **[Confirm / Edit]**"
    3.  User clicks **Confirm**.
    4.  AI executes `POST /tasks`.

### 3.3. The "Privacy Filter" Rule
> *Deleted content is dead to the AI.*

-   **Logic**: If `screenshot.deleted = true`, the vector embedding for that screenshot description is **hard-deleted** from the Vector DB immediately.
-   **Guarantee**: The AI can never reference a deleted screenshot in a summary or report.

---

## 4. Audit & Transparency

Admins have full visibility into AI usage for compliance.

| Audit Field | Description |
| :--- | :--- |
| **Timestamp** | ISO 8601 UTC. |
| **Actor** | User ID initiating request. |
| **Prompt** | The text query (Sanitized for PII). |
| **Tools Used** | e.g., `tool_sql_query`, `tool_doc_search`. |
| **Resources** | IDs of tasks/docs accessed to generate answer. |

---

**End of Functional Specs**
