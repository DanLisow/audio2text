import * as fs from "fs";
import { dirname, join } from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const AUDIO_DIR = join(__dirname, "..", "..", "audio");

export async function downloadFileFromURL(audioID, fileURL) {
  const filePath = join(AUDIO_DIR, `${audioID}.wav`);
  const writer = fs.createWriteStream(filePath);

  try {
    const response = await axios({
      url: fileURL,
      method: "GET",
      responseType: "stream",
    });

    response.data.pipe(writer);

    return new Promise((resolve, reject) => {
      writer.on("finish", () => resolve(filePath));
      writer.on("error", reject);
    });
  } catch (error) {
    throw new Error(`Не удалось скачать файл: ${error.message}`);
  }
}
