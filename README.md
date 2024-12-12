## Setting Up Infrastructure

### Overview
The infrastructure for this exercise consists of the following services:

- Zookeeper cluster
- Kafka broker
- Python-Kafka data producer
- Spark master
- Spark worker A
- Spark worker B
- Streamlit Visualization Server

![infra_diagram](https://github.com/user-attachments/assets/7b1237ba-bf0a-4f8e-a464-e8c9b1eac136)


### Building and Deploying

Navigate to the app/resources folder:

```
cd app/
```

We are going to zip the resources folder. It will be used as a python package for pyspark. Then, we will return to the root of the repository.

```
zip -r resources.zip resources
cd ../../
```

Now to actually build the services, go to the infrastructure folder:

```
cd infrastructure
```

#### Building the spark cluster image
Here, you will find a `Dockerfile` containing the instructions to setup an Apache Spark 3.5.3 image. To build this image enter the following command in your terminal:

```
cd spark_cluster 
docker build -t apache-spark:3.5.3 .
```

Return

```
cd ..
```

#### Building the streamlit server image

```
cd streamlit_server
docker build --build-context streamlit_app=../../app -t streamlit-server:1.0.0 .
```

Return 

```
cd ..
```
#### Firing up the infrastructure

You will see a Docker Compose file called `compose.yml`. This file contains the definition of the services and networking to start the infrastructure. Start the infrastructure with non-binding mode using:

```
docker compose up -d
```


### Submitting Spark Jobs

To get the name of the spark container, enter the following command:

```
spark_master_container=$(docker ps --filter "name=spark-master" --format "{{.Names}}")
```

Enter this command to launch the pyspark job to receive raw messages and perform transformations:

```
docker exec -it "$spark_master_container" /bin/sh -c "
/opt/spark/bin/spark-submit --name 'user_login_clean' \
    --master spark://spark-master:7077 \
    --py-files /opt/spark-apps/resources.zip \
    --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.3 \
    --total-executor-cores 1 \
    /opt/spark-apps/data_processing/user_login_clean.py
"
```

Open a separate terminal and again into the spark cluster:

```
docker exec -d -it "$spark_master_container" /bin/sh -c "
/opt/spark/bin/spark-submit --name 'user_login_stats' \
    --master spark://spark-master:7077 \
    --py-files /opt/spark-apps/resources.zip \
    --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.3 \
    --total-executor-cores 1 \
    /opt/spark-apps/data_processing/user_login_stats.py
"
```

check in http://localhost:9090/ that spark is running the applications. You can see each job beign assigned to different workers.
Now, allow 2 or 3 minutes to pass while Kafka server assigns partitions to the subscribers and the spark workers do their thing. This will allow the visualization server to start
getting the data after it was processed and aggregated.

Finally, visit http://localhost:10501 to check the streaming dashboard.

Enjoy!


![dashboard_gif](https://github.com/user-attachments/assets/571b039d-e7a0-4742-b32e-4681c31b1d7e)


### Cleaning the environment
To remove all of the services you have to be located in the infrastructure folder. Then enter the command:

```
docker compose down
```

Allow a couple of seconds for Docker to clean everything.
