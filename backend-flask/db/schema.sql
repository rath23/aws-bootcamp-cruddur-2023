-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
-- DROP TABLE IF EXISTS public.users;
-- DROP TABLE IF EXISTS public.activities;

-- CREATE TABLE IF NOT EXISTS public.schema_information (
--   last_successful_run text,
--   last_migration_file text
-- );

-- CREATE TABLE public.users (
--   uuid UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
--   display_name text NOT NULL,
--   handle text NOT NULL,
--   email text NOT NULL,
--   cognito_user_id text NOT NULL,
--   created_at TIMESTAMP default current_timestamp NOT NULL
-- );

-- CREATE TABLE public.activities (
--   uuid UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
--   user_uuid UUID NOT NULL,
--   message text NOT NULL,
--   replies_count integer DEFAULT 0,
--   reposts_count integer DEFAULT 0,
--   likes_count integer DEFAULT 0,
--   reply_to_activity_uuid integer,
--   expires_at TIMESTAMP,
--   created_at TIMESTAMP default current_timestamp NOT NULL
-- );

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
DROP TABLE IF EXISTS public.users;
DROP TABLE IF EXISTS public.activities;
DROP TABLE IF EXISTS public.schema_information;

-- Track migration state
CREATE TABLE public.schema_information (
  id SERIAL PRIMARY KEY,
  last_successful_run BIGINT,
  last_migration_file TEXT
);

-- Insert an initial row so migrations can read something
INSERT INTO public.schema_information (last_successful_run, last_migration_file)
VALUES (0, '');

-- Users table
CREATE TABLE public.users (
  uuid UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  display_name TEXT NOT NULL,
  handle TEXT NOT NULL,
  email TEXT NOT NULL,
  cognito_user_id TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT current_timestamp NOT NULL
);

-- Activities table
CREATE TABLE public.activities (
  uuid UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_uuid UUID NOT NULL REFERENCES public.users(uuid) ON DELETE CASCADE,
  message TEXT NOT NULL,
  replies_count INTEGER DEFAULT 0,
  reposts_count INTEGER DEFAULT 0,
  likes_count INTEGER DEFAULT 0,
  reply_to_activity_uuid UUID REFERENCES public.activities(uuid) ON DELETE CASCADE,
  expires_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT current_timestamp NOT NULL
);
