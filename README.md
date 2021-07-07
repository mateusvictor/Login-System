# Login System
Login / registration system that records user information such as username, email, password and last login to an SQL database (IBM Db2) in the cloud.

The objective of this simple project is to understand how to create queries against a table in SQL language and how to use an API (ibm_db) in Python for database manipulation.

## How to use it?
First, you must create an account in the IBM cloud and choose the IBM Db2 service. After that, you can obtain your credentials and change the contents of the variables on lines 10 and 11 with your ID and password, respectively.

### Creating a table 
The project uses only a table called users, so if you want to create with the same columns and data types, run <a href = "https://github.com/mateusvictor/Login-System/blob/main/create_table. sql ">create_table.sql</a> file in the database console.

## Program screenshots

### Menu
<img src="https://github.com/mateusvictor/Login-System/blob/main/screenshots/menu.jpg" width="800" height="600">

### Login mode
<img src="https://github.com/mateusvictor/Login-System/blob/main/screenshots/login_mode.jpg" width="800" height="600">

### Register mode
<img src="https://github.com/mateusvictor/Login-System/blob/main/screenshots/register_mode.jpg" width="800" height="600">""

### ADM mode - print users
<img src="https://github.com/mateusvictor/Login-System/blob/main/screenshots/adm_mode.jpg" width="825" height="525">

Copyright (c) 2020 Mateus Victor