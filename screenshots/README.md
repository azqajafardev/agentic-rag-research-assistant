# Screenshots

No screenshots are committed yet - they were not auto-generated because
doing so would mean fabricating "real" product screenshots without a live
LLM key in the environment this project was built in (a real chat answer
needs `LLM_API_KEY` configured; see the root README). Capture these
yourself before publishing so the README shows the app as it actually
behaves, not a mock.

Run both servers locally (or `docker compose up --build`), then capture:

| # | File name | Screen | What to show |
|---|---|---|---|
| 1 | `01-dashboard.png` | Dashboard | Stats (document/chat counts), recent activity |
| 2 | `02-documents.png` | Documents | A few indexed documents with status badges |
| 3 | `03-upload.png` | Upload modal | Mid-upload or the drag-and-drop state |
| 4 | `04-chat-new.png` | New chat | Empty chat with a document selected |
| 5 | `05-chat-answer.png` | Grounded answer | A real question + grounded answer in the chat pane |
| 6 | `06-sources.png` | Evidence panel | The source cards (page numbers, similarity scores, evidence snippet) for the answer above |
| 7 | `07-no-evidence.png` | No-evidence state | A question the documents don't cover, showing the honest "couldn't find evidence" response |
| 8 | `08-history.png` | Conversation history | The history/conversations list with more than one past chat |

Then reference them from the root `README.md`'s Screenshots section, e.g.:

```markdown
| Dashboard | Documents |
|---|---|
| ![Dashboard](screenshots/01-dashboard.png) | ![Documents](screenshots/02-documents.png) |
```

Keep images reasonably sized (PNG, ~1200-1600px wide) so the README stays
fast to load.
