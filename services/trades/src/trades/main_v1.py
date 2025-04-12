from quixstreams import Application

app = Application(
    broker_address='localhost:31234',
    consumer_group="silas"
)

# Define a topic "my_topic" with JSON serialization
topic = app.topic(name="silas-topic", value_serializer='json')

with app.get_producer() as producer:

        while True:
            event = {"id":"1","text":"Example topic to kafka"}
            message = topic.serialize(key=event["id"], value=event)
            producer.produce(
                topic=topic.name,
                value=message.value,
                key=message.key
            )
