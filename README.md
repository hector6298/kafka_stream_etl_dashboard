# Streaming ETL and Real-Time Dashboard

This is an exercise to showcase streaming ETLs with Spark-Kafka, and real-time visualizations using Streamlit.
The application consumes user login events, processes them, and displays them in a real-time map to quantify logins per state.

## Overview of architecture
Find in-depth documentation [here](https://github.com/hector6298/kafka_stream_etl_dashboard/blob/main/docs/architecture_overview.md). It contains a description of the data flow, the rationale of the design choices, and other considerations.

![infra_diagram](https://github.com/user-attachments/assets/7b1237ba-bf0a-4f8e-a464-e8c9b1eac136)

## Deploying the infrastructure and processes
--- 
**IMPORTANT: Before we start!!!!!!!**
- Use Linux or MacOS with a bash terminal to run everything. Please avoid Windows. It might work using Windows Subsystem for Linux, but I have not tested it in that environment.
- You need Docker to be able to build and run this application. Please download the latest version [here](https://docs.docker.com/get-started/get-docker/). You need at least Dockerfile 1.4 and Buildx v0.8+ for this app, so please be sure to have Docker up-to-date.
- You also need Python 3.10. Get it [here](https://www.python.org/downloads/release/python-3100/).
- Git to clone the repo. Check the downloads [here](https://git-scm.com/downloads).
- Make sure to have the `zip` command available before starting. If not, get it using `sudo apt install zip`
---
Open a terminal, clone this code repository, and navigate to it:

```
git clone https://github.com/hector6298/kafka_stream_etl_dashboard.git
cd kafka_stream_etl_dashboard
```

There are two ways of deploying everything. I made a bash script called `deploy.sh` and the other is manually deploying everything.


### Automated deployment with `deploy.sh`

If you are in the root of this repository, simply enter the command:

```
sh deploy.sh
```

It will launch everything for you. **Please allow some minutes so that the Docker images are built and run**. Be patient!
Depending on your internet connection and machine, it can vary from 4 to 10 minutes the first time.

After the services are deployed, visit the following sites:

- http://localhost:9090/ This is the Spark UI, it should have two running applications.
- http://localhost:10501/ This is the real-time dashboard that contains the number of visits per state. hover the mouse over each state to get the count.


Please let the consumers subscribe to topics and start processing the data. You should start seeing data in the dashboard after one to two minutes of deployment!

![dashboard_gif](https://github.com/user-attachments/assets/571b039d-e7a0-4742-b32e-4681c31b1d7e)


### Manual deployment

Please refer to the [following document](https://github.com/hector6298/kafka_stream_etl_dashboard/blob/main/docs/manual_deployment.md). It has all the instructions you need.


## Inspecting messages
If, in addition to the dashboard, you want to see the actual messages. You can use the script `kafka_msg_display.py`.
In your terminal, install the `kafka-python` library:

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


## Organization of this code repository

Navigate to [this page](https://github.com/hector6298/kafka_stream_etl_dashboard/blob/main/docs/code_organization.md) to learn about the organization of this code repository.

## Production considerations (Additional questions section)

Navigate to [this page](https://github.com/hector6298/kafka_stream_etl_dashboard/blob/main/docs/additional_questions.md) to learn about production considerations to take this application to the next level.



