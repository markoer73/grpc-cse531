# ASU CSE531 First Assignment

The goal of this project is to build a distributed banking system that allows multiple customers to withdraw or deposit money from the multiple branches in the bank. We assume that there are no concurrent updates on the same resources (money) in the bank, and no customer accesses multiple branches. Each branch maintains a replica of the money that needs to be consistent with the replicas in other branches. customer only communicates with only a specific branch that has the same unique ID with the customer. Although each customer independently updates a specific replica, the replicas stored in each branch need to reflect all the updates made by the customer. 

This is an assignment from Arizona State University (ASU), March 2021.

![external-content duckduckgo com](https://user-images.githubusercontent.com/22913212/112785808-29a17880-9055-11eb-8014-d637183ab0a0.png)

How to run the project?

The project has been developed and tested on Ubuntu 20.04.2 LTS and Python 3.8.  It may work with other Python and Linux versions, but they have not been tested for this assignment. The operative system was a freshly installed VM running on VMware Workstation 16.1.0.

First of all, checkout the whole project from the "Master" Branch.  Then, there are two possible ways to proceed:

1. Linux command line.  Change to the directory "grpc" and execute ./run_exercise.sh - this should setup the virtualenv, reference the libraries already included in the  and install all eventually missing libraries.  It may fail if virtualenv is not installed in the system and the current users does not have permissions to install it.

2. Use Microsoft Visual Studio.  In this case, change to the same directory "grpc" and execute "code".  If you have Visual Studio installed, it should bring up the current environment and configuration.


