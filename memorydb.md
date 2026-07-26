# Memory DB

## Project Intent

Kamara AI appears to be a live tutoring platform with a shared whiteboard, microphone streaming, and Gemini Live orchestration.

The intended loop looks like this:

1. Frontend opens a websocket session for a student and session id.
2. Frontend streams microphone audio and whiteboard snapshots to the backend.
3. Backend forwards those inputs to Gemini Live.
4. Gemini returns voice, text, and tool calls.
5. Backend sends audio/text/tool results back to the frontend over the same websocket.
6. Frontend updates the whiteboard and plays assistant audio.

## Files Inspected

- [backend/connection/websocket.py](./backend/connection/websocket.py)
- [backend/kamara/tutor/tutor.py](./backend/kamara/tutor/tutor.py)
- [backend/kamara/tutor/task_handler.py](./backend/kamara/tutor/task_handler.py)
- [backend/kamara/tutor/response_handler.py](./backend/kamara/tutor/response_handler.py)
- [backend/kamara/tutor/toolset/tools.py](./backend/kamara/tutor/toolset/tools.py)
- [backend/connection/connect_manager.py](./backend/connection/connect_manager.py)
- [backend/connection/database.py](./backend/connection/database.py)
- [public/app/routes/pages/ongoing/learning.tsx](./public/app/routes/pages/ongoing/learning.tsx)
- [public/app/routes/pages/ongoing/liveBoard.tsx](./public/app/routes/pages/ongoing/liveBoard.tsx)
- [public/app/routes/pages/dash-component/tldraw.tsx](./public/app/routes/pages/dash-component/tldraw.tsx)
- [public/app/routes.ts](./public/app/routes.ts)

## Current Architecture Notes

- The main live tutoring websocket route is `/ws/api/v1/live`.
- The backend verifies the bearer token, loads the session context from Supabase, then starts the Gemini Live agent.
- The backend inbound worker expects:
  - binary frames for microphone PCM audio
  - text JSON frames for `canvas_snapshot_text` and `canvas_snapshot_vision`
- The backend outbound worker sends:
  - `assistant_text`
  - raw audio bytes
  - `interrupted`
  - `tool_call`
- The frontend live tutoring page already has logic for:
  - opening the websocket
  - sending mic audio
  - sending canvas snapshots
  - playing returned assistant audio
  - logging assistant text and tool events

## Important Findings So Far

### 1. There are two websocket client implementations

- `public/app/routes/pages/ongoing/learning.tsx` is the full live tutoring client.
- `public/app/routes/pages/dash-component/tldraw.tsx` is a board-only websocket client.
- This duplication can make debugging confusing because not every page uses the full voice + canvas pipeline.

### 2. Board and voice now share the same websocket broadcast path

- The backend now broadcasts `assistant_text`, raw audio bytes, `interrupted`, and whiteboard `tool_call` events through the connection manager.
- That keeps the voice session and the board-only session in sync even when they are separate browser sockets.
- The board socket also reconnects cleanly after close or error instead of getting stuck on a stale connection object.

### 3. Canvas snapshots are intentionally throttled on the backend

- `task_handler.py` drops `canvas_snapshot_text` and `canvas_snapshot_vision` frames if they arrive too quickly.
- The current gate is still 2.5 seconds.
- The frontend snapshot debounce was increased to 2.6 seconds so it is less likely to outrun the backend gate.
- The backend now logs when mic and canvas frames actually arrive, which should make inbound visibility much clearer.

### 4. Tool-call payload shape likely does not match the frontend handler

- Backend tool execution returns JSON shaped like:
  - `{"type": "tool_call", "name": ..., "action": ..., "data": ..., "payload": ...}`
- The frontend live tutoring page and board-only client now accept both direct `action` payloads and nested `tool_call.payload` payloads.
- Line commands now preserve `line_type` so curve-vs-straight rendering is consistent.

### 5. Visibility is uneven

- Several historical code blocks and duplicated sections still exist in `task_handler.py` and `response_handler.py`.
- Inbound logging is active again for mic and canvas frames, which makes it easier to tell whether frames are missing, being dropped, or simply not logged.

## Working Hypothesis

The strongest current hypothesis is that the live system is partly working, but the websocket contract is fragmented:

- audio out from Gemini to the frontend is working
- assistant text is broadcast to every active socket for the student
- whiteboard/tool execution is broadcast to every active socket for the student
- the backend throttle is still suppressing some canvas traffic by design
- the main remaining risk is deployment environment drift, not the in-repo websocket contract

## Latest Log Evidence

- The pasted server logs show repeated Gemini response packets and audio byte delivery to the browser.
- The pasted logs do not show inbound browser mic or canvas frames reaching the backend.
- That absence is not conclusive by itself because the strongest inbound logging in `task_handler.py` used to be muted in the active code path.
- The logs therefore still support "outbound is alive, inbound visibility is weak" more than they prove "frontend sends nothing."

## Latest Docs Notes

- Official Gemini Live docs confirm that input audio should be raw 16-bit PCM at 16kHz with `audio/pcm;rate=16000`.
- Official Gemini Live docs confirm that video frames should be sent as individual images and that Live API output audio is typically 24kHz.
- Official Gemini Live docs say tool calls must be handled manually with `FunctionResponse` objects and sent back through the session.
- Official tldraw docs confirm that `Editor.createShape` and `Editor.createShapes` are valid APIs.
- Official tldraw docs also confirm that line shapes require explicit `points` data, not just `id/x/y`.
- That last point is important because the current line tool payloads in this repo do not appear to populate line points, which can explain why board tool calls are not rendering correctly.

## No-Code State

## Implemented Fixes

- Broadcast assistant audio/text and board tool events through the connection manager so multiple sockets for the same student stay in sync.
- Updated the board-only websocket client so it can reconnect cleanly after close/error instead of getting stuck on a stale socket reference.
- Updated the live tutor frontend to treat `tool_call` messages as real board commands when they include a board payload.
- Updated the board-only websocket client to accept both direct board commands and nested `tool_call.payload` commands.
- Changed the line tool rendering path to create an actual tldraw line shape with explicit points, spline mode, and style props.
- Updated backend tool emission so Gemini receives one clean receipt batch per tool turn instead of duplicate cumulative receipts.
- Added inbound websocket logging for mic and canvas frames so transport issues are easier to distinguish from rendering issues.
- Increased the board snapshot debounce so the frontend is less likely to outrun the backend canvas gate.

## Verification Notes

- Backend Python syntax check passed with `python -m py_compile` on the edited tool file.
- Frontend TypeScript typecheck could not complete because the workspace Node tooling hit `EPERM: operation not permitted, lstat 'C:\\Users\\DELL'`.
- That verification failure appears environment-related rather than a proven source error, but it should still be rechecked in a healthier shell if possible.

This file is a memory note so another agent can pick up the same context quickly.
