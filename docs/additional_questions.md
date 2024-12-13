# Additional questions

## How would you deploy this application in production?
It depends on the team.

If IT staff is available and specialized in maintaining cloud infrastructure, we could deploy the Kafka and Spark clusters in Kubernetes services on a major cloud provider.
Each cluster would have its namespace. The downside is that the software components need to be constantly updated and Kubernetes has to be fine-tuned to handle the workloads efficiently. It gets even more complex as we need development/test/production environments.

If the organization wants to avoid managing the services by itself and save money from IT personnel, then we could deploy:
- An Azure Event Hub with a reasonable amount of partitions and throughput units to handle event brokerage and parallelism. It is compatible with the Kafka RPC protocol.
- For the compute engine, Azure Databricks provides managed compute clusters already preloaded with Pyspark, Delta Lake, and data catalog features. It also has orchestration features which will be truly helpful as the application grows and evolves.
- Azure Data Lake Storage Gen 2 to store logs, checkpoints, and to have an inmutable storage area for raw data. The last one is highly valuable when data models in further layers change definitions. So then we could reprocess from the immutable raw area without loss of historical data.
- A container registry and container instance to allocate the visualization server.

This last one is the approach I would choose. I would have three resource groups (dev/test/prod), each with the list of services mentioned above.


## What other components would you want to add to make this production-ready?

### Standard software development practices:
- Maintain dev/test/prod environments and a repository to version control the code. Three branches dev/test/prod, with every feature requiring a new feature branch. To merge a feature, the developer must create a Pull Request to dev which has to be reviewed and approved. Once approved, it is merged into dev.  
- To move new features from dev to test, there has to be a comprehensive and automated testing suite.
    - Unit tests for utility functions, individual processing components, connectors, etc.
    - Integration tests for data pipelines using a reduced data set (smaller than prod)
- Once the tests pass along with the code review, the pull request is approved and the branch is merged. Same process to merge from test to prod.
- CI/CD pipelines: To automate tests and deployments. Avoid human error when updating the infrastructure with newer software or features.

#### Scalability:
- Tune up spark configuration to keep up with demand. Refer to **How can this application scale with a growing dataset?** below.
- Enable the auto-inflate feature in event hubs to accommodate increased throughput. 
- Use multiple topic partitions to parallelize data processing.

#### Monitoring and alerting
- Add logging capabilities to our code. Store logs from code, event hubs, and spark clusters to analyze:
    - Infrastructure uptime and performance
    - Workload status
- Add alerts when workloads fail.

#### Security
- Implement access control lists for event hub topics, databases, tables, and files in storage so that only the required users have access.
- Maintain compliance with data protection regulations by anonymizing data or implementing pseudonyms if plain rows are needed. Hash fields like
IP addresses in the case of this exercise.
- Restrict access to the visualization server using authentication through an active directory.

#### Orchestration
- Use more robust orchestration. For this exercise, I only included a bash script that deploys everything. But in production, Databricks can orchestrate streaming jobs, or tools such as Dagster can also be used for orchestration.

#### Data Quality and Governance
- Include data quality frameworks to test assumptions or expectations about the data. Great expectations package is a good tool for this purpose
- Maintain a well-documented data catalog so that data assets can be easily discoverable. In this exercise, I only moved data between Kafka topics, but in production, I would store the processed and aggregated data in tables. These tables can then be tested for data quality and be of service to data consumers.
- Include a freshness check, to avoid stale data.

#### Redundancy for high availability and fault tolerance
- Have an operating replica of the visualization server, so that in the case of failure of the primary server, the backup can take over.


## How can this application scale with a growing dataset?
- With increasing amount of streaming data we can add partitions to the topics to allow multiple parallel subscribers to consume the data from the same topic. 
- With spark cluster, we don't have to worry about implementing a framework to consume from the topic in parallel, the spark structured streaming engine does that underneath. What we can do is use our monitoring tools to measure the amount of data,
then use an appropriate configuration.
    - Partitions: By default, Spark tasks will have a 1:1 mapping with Kafka partitions on a single topic. If the data increases and this setting becomes a bottleneck, we can increase the spark `minPartition` setting so that more tasks are created per Kafka topic, balancing processing.
    - `maxOffsetsPerTrigger`: Determines how many events will be read in each micro-batch trigger. Setting this option allows predictable performance for our streaming application.
    For instance, using a `maxOffsetsPerTrigger` of 10000 spark will read the same amount of messages from event hubs on a single micro-batch. If we have 4 Kafka partitions, then Spark will create a task to read 2500 messages from each partition (2500x4 = 10000)
    It is important to watch latency and throughput to tune the application. A `maxOffsetsPerTrigger` that is too high will wait longer until we have the desired amount of messages, resulting in higher latency. Conversely, having a very low `maxOffsetsPerTrigger` won't be able to keep up with the throughput.
    - It is important to monitor cluster utilization so that we can optimize the number of worker nodes, node type, and cost.

- Having communication channels and comprehensive documentation is critical to plan platform maintenance where we can increase resources to keep up with demand while users or stakeholders are aware of any outages that may occur.

