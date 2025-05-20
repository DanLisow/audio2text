import { Router } from "express";
import { getIDAudioHandler } from "../controllers/transcribe.controller.js";

const audioRouter = Router();

audioRouter.post("/transcribe", getIDAudioHandler);

export { audioRouter };
