
# Code Organization

## app/
Contains the code of the actual application.
- **data_processing**: This is where the streaming queries are defined in python scripts.
- **resources**: This folder contains data connectors and other utitilities that will be used in the data_processing folder.
- **schema_definition**: Contain json files with the definition of the structure of the dataframes. Spark will read data from kafka and will use these schemas to parse the message and convert it into DataFrame columns.
- **visualization**: Contains the code for the visualization server app.

## docs/
Relevant documentation for this exercise.
- additional_questions: Information about production considerations and design choices.
- architecture_overview: Definitions about the services used in this exercise and why they were used.
- code_organization: The current document.
- manual_deployment: Instructions to manually deploy everything in this exercise. We recommend using the script `deploy.sh`, instead.

## infrastructure/
Contains Dockerfiles, and Docker Compose definitions to deploy the services.
- **spark_cluster/**: Contains Dockerfile to build the image for a spark cluster.
- **streamlit_server/**: Contains Dockerfile to build the image of the visualization server.

## deploy.sh

A script that will deploy all the infrastructure and spark jobs for you.

## kafka_msg_display.py

A script to consume streaming messages, after everything is deployed.
to use it, while in the root of the repository, enter:

```
python3 kafka_msg_display.py --topic "user-login-stats" --bootstrap-server "localhost:29092"
```