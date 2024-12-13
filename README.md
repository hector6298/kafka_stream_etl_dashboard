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
python3 kafka_msg_display.py --topic "user-login-stats" --bootstrap-server "localhost:29092"
```

Press `Ctrl + C` to exit when done.

## Cleaning up
To stop all services after you see the demo, while you are positioned at the root of the repository, just enter:

```
cd infrastructure
docker compose down
```


## Overview of architecture
Find in-depth documenation in the following page. It contains a description of the data flow, rationale of the design choices, and othre considerations.

![infra_diagram](https://github.com/user-attachments/assets/7b1237ba-bf0a-4f8e-a464-e8c9b1eac136)

## Organization of this code repository

Navigate to this page to learn about the organization of this code repository.

## Production considerations (Additional questions section)

Navigate to this page to learn about production considerations to take this application to the next level.



