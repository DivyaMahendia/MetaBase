Create Database rip_db

create table rip_db.dbo.docs (
id int identity(1,1)not null,
country nvarchar(200),
sn nvarchar(100),
date_time nvarchar(100),
docname nvarchar(200),
link nvarchar(max),
);

alter table rip_db.dbo.docs add constraint pk_docs primary key clustered(id);

INSERT INTO rip_db.dbo.docs (country, sn, date_time, docname, link)
VALUES 
('Myanmar', 'A', '14-03-2023', 'Myanmar Coup aftermath','C:\New folder\MyanmarCoup\M_aftermath.docx'),
....
....

select * from rip_db.dbo.docs;

CREATE TABLE rip_db.dbo.userss (
    id INT IDENTITY(1,1) PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(50) NOT NULL,
    email VARCHAR(50) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT GETDATE()
);

INSERT INTO rip_db.dbo.userss (username, password, email) 
VALUES 
('Admin', 'Password#1', 'admin@gmail.com');

SELECT * from rip_db.dbo.userss




# Create a new table for logs

CREATE TABLE rip_db.dbo.loggs (
    username VARCHAR(50) NOT NULL,
	timestamp DATETIME NOT NULL DEFAULT GETDATE(),
	table_name VARCHAR(255),
	row_id INT,
    action VARCHAR(255) NOT NULL,   
);


INSERT INTO rip_db.dbo.loggs (username, timestamp, table_name, row_id, action) 
VALUES 
('Admin', '2023-07-05 21:38:56.937', 'docs', '1', 'update');


select * from rip_db.dbo.loggs;











DELETE FROM rip_db.dbo.users
WHERE username = 'Admin';



DELETE FROM rip_db.dbo.docs
WHERE id <= 72;

SELECT id, country, sn, date_time, docname, link
FROM rip_db.dbo.docs
GROUP BY sn, id, country, docname, link, date_time
ORDER BY sn, date_time DESC


SELECT id,country, sn, date_time, docname, link
FROM rip_db.dbo.docs
ORDER BY sn, date_time desc;

SELECT *
FROM rip_db.dbo.docs
ORDER BY sn, date_time desc;


SELECT FULLTEXTSERVICEPROPERTY('IsFullTextInstalled')
AS [FULLTEXTSERVICE]

USE script_db
GO

SELECT * FROM script_db.dbo.docs
WHERE CONTAINS(docname,'india')

SELECT * FROM script_db.dbo.docs
WHERE CONTAINS(sensor,'VHF')


SELECT * FROM script_db.dbo.docs
WHERE CONTAINS (*, 'india');

