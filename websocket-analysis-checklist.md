# Websocket Analysis Checklist

## Confirmed Scope

- [x] Map the backend websocket route and orchestration path
- [x] Map the frontend live tutoring websocket client
- [x] Identify duplicate websocket clients
- [x] Identify likely throttling behavior
- [x] Record the current working hypothesis in `memorydb.md`
- [x] Implement the websocket/message-contract fix pass
- [x] Update board command rendering so line shapes have real geometry
- [x] Update backend tool emission to include direct board commands
- [x] Broadcast assistant audio/text and board tool events to every active socket for the student
- [x] Make the board websocket client reconnect cleanly after close/error
- [x] Reduce canvas snapshot churn so the frontend does not outrun the backend gate

## Things To Recheck Next

- [ ] Confirm which frontend route is the real production liveboard entry point
- [ ] Confirm the correct production websocket hostname in deployment
- [ ] Confirm whether the frontend now receives and applies the new direct `action/data` board payloads
- [ ] Confirm whether the frontend ever receives `assistant_text` in practice or only audio
- [ ] Confirm whether canvas snapshot messages are being sent from the browser
- [ ] Confirm whether backend logs now clearly show inbound frames, or whether frames never arrive
- [ ] Confirm whether the 2.5 second backend canvas gate is still suppressing useful updates
- [ ] Re-run frontend typecheck in a shell that does not hit `EPERM` on `C:\\Users\\DELL`

## Likely Failure Points

- [x] Hostname mismatch between frontend websocket URLs
- [x] Mismatch between backend tool payload shape and frontend board command parser
- [x] Snapshot frequency too high for backend gate
- [x] Duplicate websocket clients causing confusion over which path is active
- [ ] Missing or stale browser access token
- [ ] Session id missing or not matching the database record

## Debug Questions For The Next Pass

- [ ] Is the browser actually sending binary mic chunks after the mic toggle?
- [ ] Is the browser actually sending `canvas_snapshot_text` and `canvas_snapshot_vision` after board edits?
- [ ] Are backend frames arriving but being dropped by the 2.5 second gate?
- [ ] Are Gemini tool calls returning the same shape that the frontend expects?
- [ ] Is the frontend connected to the same backend host in development and production?

## Notes For Future Agents

- Do not change behavior yet unless the websocket contract is verified end-to-end.
- Prefer fixing the message contract and route alignment before adding more logging noise.
- The backend is already designed to throttle some canvas traffic, so flooding may be intentional rather than a bug.
- The current code now sends both a direct board command and a nested tool payload so the frontend has a compatibility path either way.
