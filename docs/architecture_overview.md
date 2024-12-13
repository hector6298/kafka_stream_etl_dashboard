# Overview of architecture
The infrastructure for this exercise consists of the following services orchestrated by Docker Compose:

- Zookeeper Cluster
- Kafka Broker
- Python-Kafka data producer
- Spark Master
- Spark Worker A
- Spark Worker B
- Streamlit Visualization Server

![infra_diagram](https://github.com/user-attachments/assets/7b1237ba-bf0a-4f8e-a464-e8c9b1eac136)

## The Data flow

The data flow starts with a Kafka producer service written in Python. It sends user login messages to the topic `user-login`.
Then a spark-submit job called `user_login_clean` subscribes to that topic to consume messages continuously, using spark structured streaming. Some transformations are performed on the stream to clean the data:
- Convert Unix timestamp into datetime format for column `timestamp`
- For the column `locale`, if the value in a row is null, it is transformed to `UNK`, for unknown.
- For the column `device_type`, the string is converted to lowercase and any possible whitespace is removed to standardize the device type.

The transformed data is published to another topic called `user-login-clean`. Note that the name is the same as the job to maintain consistency.

A second spark-submit job called `user_login_stats` subscribes to the `user-login-clean` topic and generates sliding window aggregates for the number of users per US state in a given time window. This aggregated data is published to the topic `user-login-stats`.

Finally, the Streamlit server uses the python-kafka library to consume from `user-login-stats`. Then, it adds the visits per state and presents it in a real-time dashboard.

#### Why would you have a second process aggregating the data? why not doing it directly in the visualization server?
Imagine that we are dealing with hundreds of thousands of messages. The visualization server would not be able to keep up with the throughput of data. If we do sliding window aggregations,
we will only generate a single data point per window of time and state which can be easily consumed by a visualization server that consists of a single process.

## Description of the services
Here is a brief overview of the services, as well as the reason for including a spark cluster, decoupled data lake, and a visualization server in a separate service.

### Zookeeper Cluster
Apache Zookeeper controls the cluster underneath Kafka. It manages service discovery, cluster topology, and the health of the cluster.
This service will work in the backend, we won't be touching anything about it.

### Kafka Broker
Handles the connections between producers and consumers (clients) and manages partitions, consumer groups, and streaming offsets.
We will be sending and receiving data from Kafka in a continuous flow of data.

Why Kafka instead of sending the data to the other services directly?
Recall that in production we might face thousands (or even millions) of events in a very short period, as our application scales.
That requires scalable infrastructure that can keep up with demand. As such, clusters of multiple computers are necessary. If we were to send data
point-to-point, the process will become infeasible as machines are added to the cluster.

Instead, Kafka can receive those messages coming from any producer of data and serve it to any consumer. Simplifying the process. In addition,
Kafka organizes these messages into topics so that producers can direct their messages to a specific topic and consumers can listen to only the data they need.

### Python-Kafka data producer
This service is going to generate user login data and send it to Kafka in a topic called `user-login`.

### Spark Cluster
This will be our data processing engine. The main reason for including a spark cluster is scalability and fault tolerance. A spark cluster can handle increasingly bigger workloads as more workers are added to the cluster. We could process more data
as partitions are sent to the workers to perform distributed work.

In addition, the spark master includes a service to check the health of its workers. If one compute node fails,
then spark can automatically send spark code to other healthy workers. Moreover, spark structured streaming saves checkpoints
of the streaming state so that it can recover if the driver node fails. These characteristics ensure fault tolerance.

### Data Lake
It acts as a centralized storage area that is independent from our computing infrastructure. It allows all of the workers to send data to a centralized place. For now, it only stores the streaming checkpoints, but it can also store delta or iceberg tables to actually persist the data.

### Streamlit visualization server
A web server built with Streamlit and Kafka-Python. It uses Streamlit as it can create web apps specialized in data visualization using Python, removing the need for more complex frameworks or other languages. 

Why a separate service instead of using the same compute in the spark cluster?
Because this process would have had to share the resources with the spark driver, potentially causing failures as more workloads are added. Decoupling processes have the benefit of only having to repair the component that fails, instead of the whole monolithic infrastructure.
