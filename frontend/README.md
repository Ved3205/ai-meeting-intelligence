# Meeting Intelligence frontend

Next.js app for uploading meetings, reading summaries and transcripts, and asking questions about them.

## Run

```
npm install
npm run dev
```

Opens on http://localhost:3000. The backend must be running (default http://localhost:8000).
To use another backend address, copy `.env.example` to `.env.local` and change `NEXT_PUBLIC_API_URL`.

## Pages

- `/` dashboard with stats and recent meetings
- `/upload` upload videos and follow processing
- `/meetings` search and open meetings
- `/meetings/[id]` summary, transcript and questions for one meeting
- `/ask` ask a question across all meetings
