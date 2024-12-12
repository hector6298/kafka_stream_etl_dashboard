# Streaming ETL and Real-Time Dashboard

This is an exercise to showcase streaming ETLs with Spark-Kafka, and real-time visualizations using Streamlit.

## Deploying the infrastructure and processes

There are two ways of deploying everything. I made a bash script called `deploy.sh` and the other is manually depoying everything yourself.


### Automated deployment with `deploy.sh`

If you are in the root of this repository, simply enter the command:

```
sh deploy.sh
```

It will launch everything for you. Please allow some minutes so that the Docker images are built and run. Be patient!
Depending on your internet connection and machine, it can vary from 4 to 10 minutes the first time.
After the Docker images are built, it takes less than one minute.

After the services are deployed, visit the following sites:

- http://localhost:9090/ This is the Spark UI, it should have two running applications.
- http://localhost:10501/ This is the real-time dashboard that contains the number of visits per state. hover the mouse over each state to get the count.


Please let the consumers subscribe to topics and start processing the data. You should start seeing data in the dashboard after one to two minutes! Similar to the picture below.

![dashboard_gif](https://github.com/user-attachments/assets/571b039d-e7a0-4742-b32e-4681c31b1d7e)


### Manual deployment

Please refer to the following document. It has all the instructions you need.


## Inspecting messages
If, in addition to the dashboard, you want to see the actual messages. You can use the script `kafka_msg_display.py`.
First, you need to install the `kafka-python` library:

```
pip3 install kafka-python
```

Then, while in the root of the repository, enter:

```
python3 kafka_msg_display.py --topic "user-login-stats" --boostrap-server "localhost:29092"
```

Press `Ctrl + C` to exit when done.

## Cleaning up
To stop all services after you see the demo, while you are positioned at the root of the repository, just enter:

```
cd infrastructure
docker compose down
```


## Overview
The infrastructure for this exercise consists of the following services:

- Zookeeper Cluster
- Kafka Broker
- Python-Kafka data producer
- Spark Master
- Spark Worker A
- Spark Worker B
- Streamlit Visualization Server

![infra_diagram](https://github.com/user-attachments/assets/7b1237ba-bf0a-4f8e-a464-e8c9b1eac136)

### Description of the workflow

The workflow starts with a kafka producer service written in python. It sends user login messages to the topic `user-login`.
Then a spark-submit job called `user_login_clean` subscribes to that topic to consume messages continously, using spark structured streaming. Some transformations are performed on the stream to clean the data:
- Convert unix timestamp into datetime format for column `timestamp`
- For the column `locale`, if the value in a row is null, it is transformed to `UNK`, for unknown.
- For the column `device_type`, the string is converted to lowercase and any possible whitespace is removed to standardize the device type.

The transformed data is published to another topic called `user-login-clean`. Note that the name is the same as the job to maintain consistency.

A second spark-submit job called `user_login_stats` subscribes to the `user-login-clean` topic and generates sliding window aggregates for the number of users per US state in a given time window. This aggregated data is published to topic `user-login-stats`.

Finally, the streamlit server users the python-kafka library to consume from `user-login-stats`. Then, it adds the visits per state and presents it in a real-time dashboard.

### Description of the Services

### Zookeper Cluster
Apache Zookeper controls the cluster underneath Kafka. It manages service discovery, cluster topology, and the health of the cluster.
This service will work in the backend, we won't be touching anything about it.

### Kafka Broker
Handles the connections from producers and consumers (clients) and manages partitions, consumer groups, and streaming offsets.
We will be sending and receiving data from kafka in a continous flow of data.

Why kafka instead of sending the data to the other services directly?
Recall that in production we might face thousands (or even millions) of events in a very short period of time, as out application scales.
That requires scalable infrastructure that can keep up with demand. As such, clusters of multiple computers are necessary. If we were to send data
point-to-point, the process will become infeasible as machines are added to the cluster.

Instead, Kafka can receive those messages coming from any producer of data and serve it to any consumer. Simplifying the process. In addition,
Kafka organizes these messages into topics so that producers can direct their messages to a specific topic and consumers can listen to only the data they need.

### Python-Kafka data producer
This service is going to generate user login data and send it to kafka in a topic called `user-login`.

### Spark Master
To simulate a scalable deployment in production, we are creating a very tiny spark cluster.
The spark master will be in charge of sending spark code to the spark workers and monitor their health.

### Spark Workers A and B
These services will be in charge of executing the spark code. In our application, the spark code subscribes
to Kafka topics, process the data in a streaming fashion (using spark structured streaming) and delivering the results
to another kafka topic.

### Streamlit Visualization Server
A web server built with streamlit and kafka-python. The kafka-python client wil subscribe to a topic called `user-login-stats`
and update the counter of visits and a choropleth map of the USA with the visits per US-state.
