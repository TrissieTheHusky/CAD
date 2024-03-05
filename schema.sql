CREATE TABLE IF NOT EXISTS calls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    address TEXT,
    name TEXT,
    description TEXT,
    status TEXT,
    units TEXT,
    history TEXT
);
