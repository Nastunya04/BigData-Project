import json
import requests
import sseclient
from kafka import KafkaProducer
import time

KAFKA_TOPIC = "input"
KAFKA_SERVER = "kafka-server:9092"
WIKI_STREAM_URL = "https://stream.wikimedia.org/v2/stream/page-create"

def main():
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_SERVER,
        key_serializer=lambda k: str(k).encode("utf-8"),
        value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )

    client = sseclient.SSEClient(WIKI_STREAM_URL)
    print("\nListening to Wikimedia stream...")

    for event in client:
        if event.event == "message":
            try:
                data = json.loads(event.data)

                if "meta" in data and "domain" in data["meta"]:
                    # Try to extract a good partition key
                    key = (
                        data.get("performer", {}).get("user_id")
                        or data.get("page_id")
                        or data.get("meta", {}).get("id")
                        or str(time.time())  # fallback random-ish
                    )

                    producer.send(KAFKA_TOPIC, key=key, value=data)
                    print(f"Sent event to Kafka | key={key} | domain={data['meta']['domain']}")
            except Exception as e:
                print(f"Error processing event: {e}")
                continue
        time.sleep(0.01)

if __name__ == "__main__":
    main()
