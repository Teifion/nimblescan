BEGIN;

CREATE TABLE nimblescan_cache (
    "user" INTEGER NOT NULL,
    expires TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    content TEXT NOT NULL,
    
    PRIMARY KEY ("user"),
    FOREIGN KEY("user") REFERENCES users (id)
);

COMMIT;
