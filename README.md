Newsletter Microservices
========================

This application uses a microservices architecture. You can use it to try out testing techniques.

Starting all the services
-------------------------

There are 3 python flask applications, named:

- greeting
- newsletter
- users

For each one, named $SERVICE_NAME, start them in a separate window like this.

	cd $SERVICE_NAME/src
	python3 -m $SERVICE_NAME

## databases

* Install [MariaDB](https://mariadb.org/download). (The following instructions are for ec2 linux 2). Note - if you are prompted to give a password for the root database, leave it blank.

    sudo yum install mysql mariadb-server
    sudo systemctl start mariadb

* Install the [ODBC driver for MySQL](https://downloads.mysql.com/archives/c-odbc/)
* Create the master database using a root connection
    
    MariaDB [(none)]> create database master;

* Create the databases using the script in the users service:

    cd users
    mysql -u root < database.sql

## Testing it

Run the TextTest start script, start_texttest.bat. Note that the tests will start their own instances of the services and their own databases so you 
do not need to start them as described above in order to test.
