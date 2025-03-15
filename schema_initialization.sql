USE moviedb;

CREATE TABLE  MotionPicture 
(id INT, 
name VARCHAR(255) NOT NULL, 
rating FLOAT, 
production VARCHAR(255),
budget INT, 
PRIMARY KEY (id), 
CHECK (rating >= 0 AND rating <= 10 AND budget > 0));

CREATE TABLE Users 
(email VARCHAR(255),
name VARCHAR(255), 
age SmallInt,
PRIMARY KEY (email));

CREATE TABLE Likes 
(uemail VARCHAR(255), 
mpid INT, 
FOREIGN KEY (uemail) REFERENCES Users(email) ON DELETE CASCADE, 
FOREIGN KEY (mpid) REFERENCES MotionPicture(id) ON DELETE CASCADE, 
PRIMARY KEY (uemail, mpid));

CREATE TABLE Movie 
(mpid INT,
boxoffice_collection FLOAT, 
FOREIGN KEY (mpid) REFERENCES MotionPicture(id) ON DELETE CASCADE,
CHECK (boxoffice_collection >= 0),
PRIMARY KEY (mpid));

CREATE TABLE Series 
(mpid INT,
season_count INT,
FOREIGN KEY (mpid) REFERENCES MotionPicture(id) ON DELETE CASCADE, 
CHECK (season_count >=1), 
PRIMARY KEY (mpid));

CREATE TABLE People 
(id INT, 
name VARCHAR(255),
nationality VARCHAR(255),
dob  DATE,
gender CHAR(1),
PRIMARY KEY (id));

CREATE TABLE Role 
(mpid INT, 
pid INT, 
role_name VARCHAR(255),
FOREIGN KEY (mpid) REFERENCES MotionPicture(id) ON DELETE CASCADE, 
FOREIGN KEY (pid) REFERENCES People(id) ON DELETE CASCADE,
PRIMARY KEY (mpid, pid, role_name));

CREATE TABLE Award
(mpid INT, 
pid INT, 
award_name VARCHAR(255), 
award_year YEAR,
FOREIGN KEY (mpid) REFERENCES MotionPicture(id) ON DELETE CASCADE,
FOREIGN KEY (pid) REFERENCES People(id) ON DELETE CASCADE,
PRIMARY KEY (mpid, pid, award_name, award_year));

CREATE TABLE Genre
(mpid INT,
genre_name VARCHAR(255), 
FOREIGN KEY (mpid) REFERENCES MotionPicture(id) ON DELETE CASCADE,
PRIMARY KEY (mpid, genre_name));

CREATE TABLE Location
(mpid INT, 
zip INT, 
city VARCHAR(255), 
country VARCHAR(255), 
FOREIGN KEY (mpid) REFERENCES MotionPicture(id) ON DELETE CASCADE,
PRIMARY KEY (mpid, zip));
