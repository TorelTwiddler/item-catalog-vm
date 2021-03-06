DROP DATABASE IF EXISTS item_catalog;

CREATE DATABASE item_catalog;

\c item_catalog;


CREATE TABLE categories(
	id			SERIAL PRIMARY KEY,
	name		VARCHAR(40) NOT NULL,
	description VARCHAR(500),
	CONSTRAINT unique_name UNIQUE(name)
);


CREATE TABLE items(
	id			SERIAL PRIMARY KEY,
	name	    VARCHAR(40) NOT NULL,
	category    INTEGER REFERENCES categories(id),
	description VARCHAR(500)
);
