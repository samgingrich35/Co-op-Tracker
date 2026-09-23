-- Delete the old table (if any) so we always start fresh.
-- Warning: running init-db erases all saved applications.
DROP TABLE IF EXISTS applications;

CREATE TABLE applications (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    company      TEXT NOT NULL,
    role         TEXT NOT NULL,
    location     TEXT,
    date_applied TEXT,  -- stored as YYYY-MM-DD
    deadline     TEXT,  -- stored as YYYY-MM-DD
    posting_url  TEXT,
    status       TEXT NOT NULL DEFAULT 'interested'
                 CHECK (status IN ('interested', 'applied', 'interviewing', 'offer', 'rejected')),
    notes        TEXT,
    created_at   TEXT DEFAULT CURRENT_TIMESTAMP
);
