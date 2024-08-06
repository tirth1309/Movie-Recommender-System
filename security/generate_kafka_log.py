from kafka import KafkaConsumer, TopicPartition
from datetime import datetime, timedelta
import time

# 配置
bootstrap_servers = 'localhost:9092'
topic = 'movielog5'
group_id = 'm4-security-1'
output_file_path = 'kafka_messages.txt'

consumer = KafkaConsumer(
    bootstrap_servers=bootstrap_servers,
    auto_offset_reset='earliest',
    group_id=group_id,
    enable_auto_commit=True,
    auto_commit_interval_ms=1000
)

# 计算两天前的时间戳
two_days_ago = datetime.now() - timedelta(days=2)
timestamp_two_days_ago = int(time.mktime(two_days_ago.timetuple()) * 1000)

# 获取Topic的所有分区
partitions = consumer.partitions_for_topic(topic)
# 创建TopicPartition对象并设置时间戳
timestamps_to_search = {TopicPartition(topic, partition): timestamp_two_days_ago for partition in partitions}

# 查找offsets
offsets = consumer.offsets_for_times(timestamps_to_search)

# 设置consumer从特定offset开始消费
for tp, offset_info in offsets.items():
    if offset_info:
        consumer.assign([tp])
        consumer.seek(tp, offset_info.offset)

# 写入文件
with open(output_file_path, 'w', encoding='utf-8') as file:
    for message in consumer:
        file.write(f"{message.value}\n")
        print(f"Written message to file: {message.value}")

# 关闭consumer
consumer.close()
