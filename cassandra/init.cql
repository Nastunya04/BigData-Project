CREATE KEYSPACE IF NOT EXISTS wiki
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

USE wiki;

CREATE TABLE IF NOT EXISTS pages_by_id (
  page_id TEXT PRIMARY KEY,
  user_id TEXT,
  user_name TEXT,
  domain TEXT,
  page_title TEXT,
  created_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pages_by_user (
  user_id TEXT,
  created_at TIMESTAMP,
  page_id TEXT,
  user_name TEXT,
  domain TEXT,
  page_title TEXT,
  PRIMARY KEY (user_id, created_at, page_id)
) WITH CLUSTERING ORDER BY (created_at DESC);

CREATE TABLE IF NOT EXISTS pages_by_domain (
  domain TEXT,
  created_at TIMESTAMP,
  page_id TEXT,
  user_id TEXT,
  user_name TEXT,
  page_title TEXT,
  PRIMARY KEY (domain, created_at, page_id)
) WITH CLUSTERING ORDER BY (created_at DESC);

CREATE TABLE IF NOT EXISTS pages_by_time (
  date_hour TEXT,
  user_id TEXT,
  user_name TEXT,
  page_id TEXT,
  domain TEXT,
  page_title TEXT,
  created_at TIMESTAMP,
  PRIMARY KEY (date_hour, user_id, created_at, page_id)
) WITH CLUSTERING ORDER BY (user_id ASC, created_at DESC);

-- ========== Category A: Domain statistics by hour ==========
CREATE TABLE IF NOT EXISTS domain_hour_stats (
    date_hour TEXT,
    domain TEXT,
    count_pages INT,
    PRIMARY KEY ((date_hour), domain)
);

-- ========== Category A: Pages created by bots ==========
CREATE TABLE IF NOT EXISTS bot_domain_stats (
    time_start TEXT,
    domain TEXT,
    count_bots INT,
    PRIMARY KEY ((time_start), domain)
);

-- ========== Category A: Top 20 users ==========
CREATE TABLE IF NOT EXISTS top_users_stats (
    time_start TEXT,
    time_end TEXT,
    user_id TEXT,
    user_name TEXT,
    page_titles LIST<TEXT>,
    page_count INT,
    PRIMARY KEY ((time_start, time_end), page_count, user_id)
) WITH CLUSTERING ORDER BY (page_count DESC);
