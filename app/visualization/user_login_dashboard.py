from kafka import KafkaConsumer
import json
import plotly.express as px
import streamlit as st
import pandas as pd


def setup_streamlit_dashboard():
    """
    Sets up the Streamlit dashboard layout and title.
    
    Returns
    -------
    tuple
        A tuple containing two Streamlit metric placeholders for unique users and distinct devices.
    """
    st.set_page_config(
        page_title="Kafka Streaming Dashboard",
        layout="wide"
    )
    st.title("Kafka Streaming Dashboard: User Login Stats")
    
    # Create metric placeholders
    col1, col2 = st.columns(2)
    user_vists_metric = col1.metric("User Visits", "Loading...")

    # Placeholders
    latest_row_placeholder = col1.empty()
    map_placeholder = col2.empty()

    return user_vists_metric, latest_row_placeholder, map_placeholder


def initialize_kafka_consumer(bootstrap_server, topic):
    """
    Initializes a Kafka consumer for the specified topic.
    
    Parameters
    ----------
    bootstrap_server : str
        The Kafka bootstrap server address.
    topic : str
        The name of the Kafka topic to subscribe to.

    Returns
    -------
    KafkaConsumer
        A KafkaConsumer instance subscribed to the specified topic.
    """
    return KafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_server,
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        auto_offset_reset='latest',
        enable_auto_commit=True
    )


def update_metrics_from_kafka(consumer, 
                              topic,
                              user_vists_metric, 
                              latest_row_placeholder, 
                              map_placeholder):
    """
    Listens to Kafka messages and updates Streamlit metrics in real time.
    
    Parameters
    ----------
    consumer : KafkaConsumer
        The Kafka consumer instance.
    topic: str
        The Kafka topic.
    user_vists_metric : st.metric
        Streamlit metric placeholder for user visits.
    latest_row_placeholder : st.empty
        Streamlit empty placeholder where the latest row form kafka will arrive.
    map_placeholder : st.empty
        Streamlit empty placeholder where the map of user counts will be.
    """
    st.markdown(f"### Listening to Kafka Topic: `{topic}`")
    
    # List of all U.S. state abbreviations
    states = [
        "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA",
        "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
        "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT",
        "VA", "WA", "WV", "WI", "WY"
    ]

    # Initialize counter objects
    state_counts = pd.DataFrame(data={"count": 0}, index=states)
    global_user_count = 0
    global_device_count = 0

    try:
        for message in consumer:
            record = message.value

            # Extract metrics from the Kafka message
            unique_users = record.get("unique_users", 0)
            distinct_devices = record.get("distinct_devices", 0)

            # Update counter variables
            state_counts.loc[record.get("locale", "UNK"), "count"] += unique_users
            global_user_count += unique_users
            global_device_count += distinct_devices

            # Update Streamlit metrics
            user_vists_metric.metric("User Visits", global_user_count)

            # Update the latest message placeholder
            with latest_row_placeholder.container():
                st.write("Latest Record From Kafka")
                st.json(record)
            
             # Choropleth map using Plotly Express
            with map_placeholder.container():
                st.write("Choropleth map of User Visits")
               
                fig = px.choropleth(
                    state_counts,
                    locations=states,
                    locationmode="USA-states",  # Specify that locations are USA state abbreviations
                    color="count",
                    hover_name=states,
                    color_continuous_scale="Viridis",
                    scope="usa",
                    title="Count of Users per State"
                )

                fig.update_layout(height=250, margin={"r":0,"t":0,"l":0,"b":0})
                st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error in Kafka streaming: {str(e)}")


def main():
    """
    Main function to initialize the Kafka consumer and start the Streamlit dashboard.
    """
    bootstrap_server = "kafka:9092"
    topic = "user-login-stats"

    user_vists_metric, latest_row_placeholder, map_placeholder = setup_streamlit_dashboard()
    consumer = initialize_kafka_consumer(bootstrap_server, topic)
    update_metrics_from_kafka(consumer, topic, user_vists_metric, latest_row_placeholder, map_placeholder)


if __name__ == "__main__":
    main()