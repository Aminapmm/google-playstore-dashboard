SET search_path TO googleplay;

-- Developers Table
CREATE TABLE IF NOT EXISTS developers (
    developer_id VARCHAR(255) PRIMARY KEY, -- primary key
    developer_website VARCHAR(255), -- Developer's website
    developer_email VARCHAR(255)    -- Developer's email
);

-- Categories Table
CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY, -- primary key
    category VARCHAR(255) NOT NULL  -- Category name (e.g., Games, Education)
);

-- Apps Table
CREATE TABLE IF NOT EXISTS apps (
    app_id VARCHAR(255) PRIMARY KEY,                     -- Auto-incrementing primary key for apps
    app_name VARCHAR(255) NOT NULL,                -- App name
    developer_id VARCHAR(255)  REFERENCES developers(developer_id), -- Foreign key referencing developers table
    category_id INT  REFERENCES categories(category_id),   -- Foreign key referencing categories table
    rating FLOAT,                                  -- App rating (e.g., 4.5)
    rating_count BIGINT,                          -- Number of ratings received
    installs VARCHAR(50),                          -- Install count as a string (e.g., "1M+")
    minimum_installs BIGINT,                      -- Minimum number of installs
    maximum_installs BIGINT,                      -- Maximum number of installs
    free BOOLEAN NOT NULL DEFAULT TRUE,            -- Whether the app is free or not
    price FLOAT DEFAULT 0.0,                       -- Price of the app (if applicable)
    currency VARCHAR(10),                          -- Currency code (e.g., USD)
    size FLOAT,                                    -- Size of the app in MB or GB (optional)
    released TIMESTAMP,                            -- Release date of the app
    minimum_android VARCHAR(255),
	last_updated TIMESTAMP,                        -- Last updated date of the app
    content_rating VARCHAR(50),                   -- Content rating (e.g., Everyone, Teen)
    privacy_policy TEXT,                  -- URL to the privacy policy
    ad_supported BOOLEAN DEFAULT FALSE,           -- Whether the app is ad-supported or not
    in_app_purchases BOOLEAN DEFAULT FALSE,       -- Whether the app supports in-app purchases or not
    editors_choice BOOLEAN DEFAULT FALSE          -- Whether the app is an editor's choice or not
);
