import pika
import json
import logging
import time
from audio_processing.audio_main import HandleAudio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Queue:
    def start_worker():
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                connection = pika.BlockingConnection(pika.ConnectionParameters(
                    host="localhost",
                    heartbeat=600,
                    blocked_connection_timeout=300
                ))

                channel = connection.channel()

                channel.exchange_declare(
                    exchange="audio2text",
                    exchange_type="direct",
                    durable=True
                )
                channel.queue_declare(
                    queue="audio2text.transcribe",
                    durable=True
                )
                channel.queue_bind(
                    queue="audio2text.transcribe",
                    exchange="audio2text",
                    routing_key="audio2text.request"
                )

                def callback(ch, method, properties, body):
                    try:
                        logger.info(f"Получено сообщение с correlation_id: {properties.correlation_id}")

                        try:
                            payload = json.loads(body)
                            json_str = bytes(payload['data']).decode('utf-8')
                            message = json.loads(json_str)

                            print("==============================")
                            print(message)
                            print("==============================")

                            audio_path = message["file_path"]
                        except (json.JSONDecodeError, KeyError) as e:
                            logger.error(f"Неверный формат сообщения: {e}")
                            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                            return
                        
                        try:
                            start_time = time.time()
                            
                            result_text = HandleAudio.start_handle(audio_path=audio_path)

                            end_time = time.time()

                            print(f"Время выполнения: {end_time-start_time}")
                        except Exception as e:
                            logger.error(f"Ошибка обработки аудио {audio_path}: {e}")
                            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                            return

                        ch.basic_publish(
                            exchange="",
                            routing_key=properties.reply_to,
                            properties=pika.BasicProperties(
                                correlation_id=properties.correlation_id
                            ),
                            body=result_text.encode('utf-8')
                        )

                        ch.basic_ack(delivery_tag=method.delivery_tag)
                        logger.info(f"Аудио успешно обработано {audio_path}")

                    except Exception as e:
                        logger.error(f"Непредвиденная ошибка: {e}", exc_info=True)
                        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

                channel.basic_qos(prefetch_count=1)
                channel.basic_consume(queue="audio2text.transcribe", on_message_callback=callback)
                logger.info("Worker запущен, ожидание сообщений...")
                channel.start_consuming()
            
            except pika.exceptions.AMQPConnectionError as e:
                retry_count += 1
                logger.error(f"Неудачное подключение (попытка {retry_count}/{max_retries}): {e}")
                if retry_count == max_retries:
                    logger.error("Превышено максимально допустимое количество попыток переподключения")
                    raise
                time.sleep(5 * retry_count)

            except pika.exceptions.AMQPError as e:
                logger.error(f"Ошибка RabbitMQ: {e}", exc_info=True)
                raise

            except KeyboardInterrupt:
                logger.info("Worker остановлен пользователем")
                if 'connection' in locals() and connection.is_open:
                    connection.close()
                break

            except Exception as e:
                logger.error(f"Непредвиденная ошибка: {e}", exc_info=True)
                raise


