CREATE TABLE IF NOT EXISTS passengers (
    passenger_id INTEGER PRIMARY KEY,
    passenger_class SMALLINT NOT NULL CHECK (passenger_class BETWEEN 1 AND 3),
    survived BOOLEAN NOT NULL,
    age NUMERIC(5, 2) CHECK (age IS NULL OR age >= 0)
);
