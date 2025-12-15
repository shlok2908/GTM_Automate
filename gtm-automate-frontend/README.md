# GTM Automate — Frontend

Simple React (Vite) frontend for uploading GTM input files and selecting pixel type.

Quick start

1. Install dependencies:

```powershell
cd gtm-automate-frontend
npm install
```

2. Start dev server:

```powershell
npm run dev
```

3. Open `http://localhost:5173` and use the UI.

Notes

- The frontend expects a backend endpoint at `POST http://localhost:8000/upload` that accepts `multipart/form-data` with fields `pixel` and `file`.
- If your backend uses a different path/port, update the URL in `src/components/UploadForm.jsx`.
