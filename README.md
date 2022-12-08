Newsletter Microservices
========================

This application uses a microservices architecture. You can use it to try out testing techniques.
Start by installing Python 3.9

Starting all the services
-------------------------

There are 3 python flask applications, named:

- greeting
- newsletter
- users

For each one, named $SERVICE_NAME, start them in a separate window like this.
Note that the Python version should be at most 3.9 currently.

	cd $SERVICE_NAME/src
	python3 -m $SERVICE_NAME

## databases

Install [MariaDB](https://mariadb.org/download). (The following instructions are for ec2 linux 2)

    sudo yum install mysql mariadb-server
    sudo systemctl start mariadb

Create the databases using the script in the users service:

For each one:

    cd users
    mysql -u root < database.sql

## Jaeger tracing

Download and run jaeger using docker:

	docker run -d --name jaeger \
	    -p 6831:6831/udp \
    	-p 16686:16686 \
    	-p 14268:14268 \
    	jaegertracing/all-in-one:1.6

Alternatively, download jaeger binaries from [jaeger website](https://www.jaegertracing.io/download/). Unpack them and
link them under /usr/local/bin:

    sudo tar xvzf jaeger-1.26.0-linux-amd64.tar.gz  -C /opt/
    cd /usr/local/bin
    ln -s /opt/jaeger-1.26.0-linux-amd64/jaeger-all-in-one .
    
Start the jaeger-all-in-one binary then navigate to the [jaeger application](http://localhost:16686/) 


## Testing it

Run the TextTest start script, start_texttest.bat. Note that the tests will start their own instances of the services and their own databases so you 
do not need to start them as described above in order to test.
