Cloud-Hosted Python Web App with SQLite on AWS

Abstract

This project is about building a small web application in Python, using a SQLite database, and deploying it to the AWS cloud. 
The idea is to take something simple that works locally and get it running on a cloud environment so it can be accessed over the internet. 
The focus is on understanding how the backend, database, and cloud setup fit together rather than building a very complex app.

Introduction

The scope of this project is to design and deploy a basic web application that connects to a database and runs on AWS. 
The application will be built in Python with a lightweight web framework and will use SQLite as the database, since it is easy to set up and I already have experience with it. 
The project will cover creating routes to handle user requests, performing simple database operations (like insert, update, and read), and then deploying the application to an AWS environment.
The main goal is to get a working end-to-end pipeline: code running locally, connected to SQLite, then hosted on AWS so it is available through a browser. 
This gives practical experience with both backend development and cloud deployment.



Technologies used

Python: for writing the backend logic and handling requests and responses.

Flask (or similar Python web framework): to define routes, handle HTTP requests, and return responses.

SQLite: as the database to store application data in a simple file-based format.

Git: for basic version control and managing the project code.

Cloud technology and provider

The cloud provider for this project is Amazon Web Services (AWS). The plan is to deploy the web application on an AWS compute service 
(for example an EC2 instance) and configure it so that the app is reachable through a public URL. Basic AWS networking concepts like security groups and instance configuration 
will be used to allow web traffic to the application. If time allows, I may also look at using an S3 bucket for static files or backups, but the main focus is getting the core app and 
SQLite database running reliably on AWS.

Expected outcomes

By the end of the project, I expect to have a working web application running on AWS that can handle simple user interactions. 
The app should be able to connect to the SQLite database, store new records, and read them back through the web interface. 
I also expect to understand the basic steps of deploying a Python app from my local machine to AWS, including setting up the instance, 
configuring the environment, and troubleshooting common issues. Overall, the outcome should be a small but fully functional cloud-hosted 
application that demonstrates the full stack from code to cloud.