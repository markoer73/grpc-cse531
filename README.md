# ASU CSE531 First Assignment

The goal of this project is to build a distributed banking system that allows multiple customers to withdraw or deposit money from the multiple branches in the bank. We assume that there are no concurrent updates on the same resources (money) in the bank, and no customer accesses multiple branches. Each branch maintains a replica of the money that needs to be consistent with the replicas in other branches. customer only communicates with only a specific branch that has the same unique ID with the customer. Although each customer independently updates a specific replica, the replicas stored in each branch need to reflect all the updates made by the customer. 

This is an assignment from Arizona State University (ASU), March 2021.

![external-content duckduckgo com](https://user-images.githubusercontent.com/22913212/112785808-29a17880-9055-11eb-8014-d637183ab0a0.png)
 
