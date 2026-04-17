-- Run this in the Supabase SQL Editor (Dashboard > SQL Editor)
-- to permanently delete the old_teachers table and other unused tables.

-- Drop old_teachers table (old migration data, no longer needed)
DROP TABLE IF EXISTS old_teachers CASCADE;

-- Verify remaining tables
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public'
ORDER BY table_name;
