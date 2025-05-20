import * as axios from "axios";
import { downloadFileFromURL } from "../services/file.service.js";
import { rabbitMQClient } from "../services/rabbitmq.service.js";

const MEDIA_SERVICE_URL = process.env.MEDIA_SERVICE_URL;

export const getIDAudioHandler = async (req, res) => {
  const { audio_id } = req.body;

  if (!audio_id) {
    return res.status(400).json({ error: "Не передан ID аудиозаписи" });
  }

  try {
    const resultAudio = await axios({
      url: MEDIA_SERVICE_URL,
      method: "POST",
      data: {
        id: audio_id,
      },
    });

    const fileURL = resultAudio.data.fileURL;

    if (!fileURL) {
      return res.status(404).json({ error: "Файл не найден в базе данных" });
    }

    const filePath = await downloadFileFromURL(audio_id);

    const task = {
      audio_id: audio_id,
      file_path: filePath,
    };

    rabbitMQClient.sendToQueue(Buffer.from(JSON.stringify(task)));

    return res.status(202).send(`Файл ${audio_id} добавлен в очередь`);
  } catch (error) {
    return res.status(500).send(`Ошибка: ${error}`);
  }
};
