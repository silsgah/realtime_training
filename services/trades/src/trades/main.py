# Create an Application instance with Kafka configs
from quixstreams import Application
from loguru import logger

from kraken_api import KrakenAPI, Trade

def run(
    kafka_broker_address: str,
    kafka_topic_name: str,
    kraken_api: KrakenAPI,
):
    app = Application(
        broker_address=kafka_broker_address,
    )

    # Define a topic "my_topic" with JSON serialization
    topic = app.topic(name=kafka_topic_name, value_serializer='json')


    # Create a Producer instance
    with app.get_producer() as producer:

        while True:

            # 1. Fetch the event from the external API
            events: list[Trade] = kraken_api.get_trades()
            # event = {"id": "1", "text": "Lorem ipsum dolor sit amet"}

            for event in events:
                # 2. Serialize an event using the defined Topic 
                message = topic.serialize(
                    # key=event["id"],
                    value=event.to_dict()
                )

                # 3. Produce a message into the Kafka topic
                producer.produce(
                    topic=topic.name,
                    value=message.value,
                    # key=message.key
                )

                logger.info(f'Produced message to topic {topic.name}')

            # breakpoint()

if __name__ == "__main__":

    # create object that can talk to the Kraken API and get us the trade data in real time
    api = KrakenAPI(product_ids=['BTC/EUR'])
    
    run(
        kafka_broker_address='localhost:31234',
        kafka_topic_name='trades',
        kraken_api=api,
    )