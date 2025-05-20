import express from "express";
import * as env from "dotenv";
import { audioRouter } from "./routes/router.js";
import { rabbitMQClient } from "./services/rabbitmq.service.js";

env.config();

const expressApp = express();
const PORT = process.env.PORT || 3000;

expressApp.use(express.json());
expressApp.use(express.urlencoded({ extended: true }));
expressApp.use(audioRouter);

expressApp.listen(PORT, () => {
  rabbitMQClient.connect();

  console.log(`Сервер запущен на порту ${PORT}`);
});
