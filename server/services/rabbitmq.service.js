import * as amqp from "amqplib";
import * as axios from "axios";
import { v4 as uuidv4 } from "uuid";

class RabbitMQService {
  constructor() {
    this.connection = null;
    this.channel = null;
    this.isConnecting = false;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;

    this.replyQueue = null;
    this.pendingResponses = new Map();
    this.defaultTimeout = 600000;
  }

  async connect() {
    if (this.isConnecting) return;
    this.isConnecting = true;

    try {
      this.connection = await amqp.connect(process.env.RABBITMQ_URL || "amqp://localhost");
      this.channel = await this.connection.createChannel();

      this.reconnectAttempts = 0;
      console.log("Подключено к RabbitMQ");

      this.connection.on("close", () => {
        this.pendingResponses.forEach(({ reject }) => {
          reject(new Error("RabbitMQ connection closed"));
        });
        this.pendingResponses.clear();

        this.reconnect();
      });

      await this.initConsumer();

      return this.channel;
    } catch (error) {
      console.log(`Ошибка подключения к RabbitMQ: ${error}`);

      await this.reconnect();
      throw error;
    } finally {
      this.isConnecting = false;
    }
  }

  async reconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log("Достигнуто максимальное количество попыток переподключения");

      return;
    }

    this.reconnectAttempts++;
    const delay = Math.min(1000 * this.reconnectAttempts, 10000);

    console.log(`Попытка переподключения ${this.reconnectAttempts} через ${delay}ms`);

    setTimeout(() => this.connect(), delay);
  }

  async initConsumer() {
    if (!this.channel) throw new Error("Канал не инициализирован");

    try {
      this.replyQueue = await this.channel.assertQueue("", { exclusive: true });

      await this.channel.consume(
        this.replyQueue.queue,
        (msg) => {
          if (msg) {
            const content = msg.content.toString("utf-8");

            this.sendToService(content);

            this.channel.ack(msg);
          }
        },
        { noAck: false }
      );
    } catch (error) {
      console.error("Ошибка инициализации потребителя:", error);
      throw error;
    }
  }

  async sendToQueue(message) {
    try {
      if (!this.channel) {
        await this.connect();
      }

      const correlationID = uuidv4();

      await this.channel.assertExchange("audio2text", "direct", {
        durable: true,
      });

      this.channel.publish("audio2text", "audio2text.request", Buffer.from(JSON.stringify(message)), {
        correlationId: correlationID,
        replyTo: this.replyQueue.queue,
      });
    } catch (error) {
      console.log(`Ошибка при отправке в RabbitMQ: ${error}`);

      throw error;
    }
  }

  async sendToService(data) {
    try {
      if (!process.env.MEDIA_SERVICE_URL_SAVE_TRANSCRIPTION) {
        throw new Error("MEDIA_SERVICE_URL_SAVE_TRANSCRIPTION не объявлено");
      }

      await axios.post(process.env.MEDIA_SERVICE_URL_SAVE_TRANSCRIPTION, data, { timeout: 5000 });
    } catch (error) {
      console.error("Ошибка отправки в сервис медиа:", error);
      throw error;
    }
  }
}

export const rabbitMQClient = new RabbitMQService();
