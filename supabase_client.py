from supabase import create_client, Client

# Replace these with your actual keys from Supabase settings
SUPABASE_URL = https://zphpikwyhjeybysfpcfn.supabase.co
SUPABASE_KEY = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpwaHBpa3d5aGpleWJ5c2ZwY2ZuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI0NjgwMTgsImV4cCI6MjA2ODA0NDAxOH0.2S0VxzExFvYj56BrrcS1dH9xfV9I2Tng_S8VJFrBrS4

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

-- USERS TABLE
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL
);

-- TASKS TABLE
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    task TEXT NOT NULL,
    done BOOLEAN DEFAULT FALSE,
    due_date DATE,
    category TEXT,
    completed_date DATE
);

-- HISTORY TABLE
CREATE TABLE IF NOT EXISTS history (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    date DATE NOT NULL,
    completed INTEGER DEFAULT 0
);

-- JOURNALS TABLE
CREATE TABLE IF NOT EXISTS journals (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    entry TEXT NOT NULL,
    mood TEXT,
    date DATE NOT NULL
);

-- MEALS TABLE
CREATE TABLE IF NOT EXISTS meals (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    date DATE NOT NULL,
    meal_type TEXT,
    meal_name TEXT,
    mood TEXT
);
