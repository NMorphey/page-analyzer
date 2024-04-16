CREATE TABLE IF NOT EXISTS urls (
    id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name VARCHAR(255),
    created_at DATE
);

CREATE TABLE IF NOT EXISTS url_checks (
    id INT,
    url_id INT,
    status_code INT,
    h1 VARCHAR(255),
    title VARCHAR(255),
    description TEXT
);
