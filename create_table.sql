CREATE TABLE USERS (
	ID BIGINT PRIMARY KEY NOT NULL,
	EMAIL VARCHAR(8000) NOT NULL,
	USERNAME VARCHAR(100) NOT NULL,
	PASSWORD VARCHAR(100) NOT NULL,
	LAST_LOGIN VARCHAR(20) NOT NULL
);