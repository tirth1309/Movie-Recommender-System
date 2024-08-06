from kafka import KafkaConsumer, TopicPartition
from datetime import datetime, timedelta
import time
from data_validation.data_validator import validate_log_line


bootstrap_servers = 'localhost:9092'
topic = 'movielog5'
group_id = 'm4-security-5'
output_file_path = 'kafka_messages_2024_04_20.txt'

consumer = KafkaConsumer(
    bootstrap_servers=bootstrap_servers,
    auto_offset_reset='earliest',
    group_id=group_id,
    enable_auto_commit=True,
    auto_commit_interval_ms=1000
)

# Set the specific date to collect data from (April 20, 2024)
start_date = datetime(2024, 4, 20)
end_date = datetime(2024, 4, 21)

start_timestamp = int(time.mktime(start_date.timetuple()) * 1000)
end_timestamp = int(time.mktime(end_date.timetuple()) * 1000)

partitions = consumer.partitions_for_topic(topic)
start_offsets = {TopicPartition(topic, partition): start_timestamp for partition in partitions}
end_offsets = {TopicPartition(topic, partition): end_timestamp for partition in partitions}

# Get starting and ending offsets for each partition
start_offsets = consumer.offsets_for_times(start_offsets)
end_offsets = consumer.offsets_for_times(end_offsets)

with open(output_file_path, 'w', encoding='utf-8') as file:
    for tp, start_info in start_offsets.items():
        if start_info:
            consumer.assign([tp])
            consumer.seek(tp, start_info.offset)
            end_offset = end_offsets[tp].offset if end_offsets[tp] else None

            for message in consumer:
                if message.offset < end_offset:
                    event = message.value.decode('utf-8')
                    if validate_log_line(event):
                        values = event.split(',')
                        if 'recommendation request' in values[2]:
                            file.write(f"{message.value.decode('utf-8')}\n")
                            print(f"Written message to file: {message.value.decode('utf-8')}")
                else:
                    break

consumer.close()
