import argparse
import json
import time
from kafka import KafkaConsumer

def main():
    # Argument parser
    parser = argparse.ArgumentParser(description="Kafka Consumer Script")
    parser.add_argument("--topic", type=str, required=True, help="Kafka topic to subscribe to")
    args = parser.parse_args()
    topic = args.topic

    kafka = KafkaConsumer(
        topic,
        group_id="visualization-consumer",
        bootstrap_servers="localhost:29092",
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        auto_offset_reset='earliest',
        enable_auto_commit=False
    )

    print(f"Available topics are: {kafka.topics()}")
    print(f"Topic selected to subscribe: {topic}")
    print("Starting message retrieval...")

    try:
        # Consume messages
        for message in kafka:
            print("%s:%d:%d: key=%s value=%s" % (
                message.topic, message.partition,
                message.offset, message.key,
                message.value
            ))
    except KeyboardInterrupt:
        print("\nGracefully shutting down the Kafka consumer...")
    finally:
        kafka.close()

if __name__ == "__main__":
    main()