Newsletter Microservices
========================

This application was created to showcase the capabilities of [TextTest](https://texttest.org) for testing microservices systems.

There are 3 python flask applications, named:

- Greeting
- Newsletter
- Users

The functionality is fairly simple, it's designed to be a kind of "hello world" microservices system, or the first iteration of a more ambitious system. Only one of the services - users - has a database, the others are stateless. The services communicate with each other over http. The whole system is accessed via a public REST api on the newsletter service which is documented with Swagger.

The Newsletter api has only one endpoint - "sayHello" - which takes one parameter, a name of a person. This is someone who wants to sign up for a newsletter. At the moment the functionality for newsletters is not yet built. The system will store their name and return a greeting. 

When you call the "sayHello" endpoint:

* The Newsletter service asks the Users service to look up any information we already have on the user
* The Newsletter service asks the Greeting service to compose a suitable greeting for the user
* The greeting is returned.

The response from the Users service is slightly different depending on whether we already have this user in our database or not. If it is a new user, a new record is created for them, unless the user has a name that is on a blocklist (see the code in users.py to find out what's on the blocklist). If it's a known user, then we return more information about them and the greeting service provides a longer greeting for them. Users on the blocklist don't get a greeting.

## Prerequisites - python libraries and database installation

* Make a python virtual environment and install the dependencies from requirements.txt

* Install [MariaDB](https://mariadb.org/download). (The following instructions are for ec2 linux 2). Note - if you are prompted to give a password for the root database, leave it blank.

    sudo yum install mysql mariadb-server
    sudo systemctl start mariadb

* Install the [ODBC driver for MySQL](https://downloads.mysql.com/archives/c-odbc/)
* Create the master database using a root connection:
    
    MariaDB [(none)]> create database master;

## Testing it with TextTest

Run the TextTest start script, start_texttest.bat, to open the static GUI and browse the test cases.

There are three test cases provided, for the three main use cases:

* "AddUser" User is new, and not on the blocklist.
* "KnownUser" User is already in our database.
* "BadUser" User is new, but their name is on the blocklist.

You should verify that you can run the tests and that they pass in "Replay" mode. When you do this, TextTest will run tests in parallel up to the number of CPUs you have on your machine. Each test case runs an entirely separate instance of the whole microservices system, including separate databases. This is why the tests take a little time to run. Each test case will wait to create a new database, start three services, trigger the endpoint via swagger, collect the results and evaluate whether the test passed.

### Speeding up the tests - Running only some of the services

If you are working on, say, the logic in the Greeting service, you may not need to run the real versions of the other two service. In this case you can set those services to replay via capturemock. On the "Running" tab, there is a dropdown for each service where you can specify whether to run against the real code, or leave blank to run against recorded interactions. If you put the Users and Newsletter services to blank, the test will run much faster because it will only start the Greeting service. You will still be able to test your changes. The tests will only fail if you change something about the public interface of the service. This can be very useful when you're refactoring, or when you want to see what functionality will be impacted by a change.

## Starting all the services by hand

Create the users databases using the script in the users service. On unix:

    cd users
    mysql -u root < database.sql

On windows you can use the interactive db prompt:

    MariaDB [(none)]> source C:\Users\Administrator\workspace\newsletter-microservices\users\database.sql


For each service, (users, newsletter and greeting), here referred to as $SERVICE_NAME, start them in a separate window like this:

	cd $SERVICE_NAME/src
	python -m $SERVICE_NAME

When they are all running, you should be able to open a browser on the [Newsletter swagger api](http://localhost:5010/docs) to access the functionality.

