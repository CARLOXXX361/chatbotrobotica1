from typing import Optional, Union, Dict, Tuple, List
from pydantic import BaseModel, Field
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
import cv2
import torch
import time
from langchain.tools import BaseTool


# Cargar modelos
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
model_blip = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large").to("cuda")
model_yolo = torch.hub.load("ultralytics/yolov5", 'custom', path='yolov5s.pt', force_reload=True)

# Configuraciones
labels = model_yolo.module.names if hasattr(model_yolo, 'module') else model_yolo.names
colors = {"cellphone": (0, 0, 255), "person": (0, 255, 255)}


class PhotoDetectionInput(BaseModel):
    pass


class PhotoDetectionOutput(BaseModel):
    detected_objects: List[str]
    contexto: str


def take_photo() -> cv2.VideoCapture:
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    time.sleep(1)
    cap.release()
    return frame


def detect_objects(frame: cv2.VideoCapture) -> List[str]:
    results = model_yolo(frame)
    detections = results.pred[0]
    mask = detections[:, 4].cpu().numpy() > 0.5
    detected_objects = [labels[int(det[-1])] for det in detections[mask]]
    return detected_objects


def get_image_context(image_path: str) -> str:
    raw_image = Image.open(image_path).convert('RGB')
    inputs = processor(raw_image, "a photography of", return_tensors="pt").to("cuda")
    out = model_blip.generate(**inputs)
    return processor.decode(out[0], skip_special_tokens=True)


class PhotoDetectionTool(BaseTool):
    name = "photo_detection"
    description = ("Una herramienta avanzada para la detección visual de personas u objetos"
                   )
    def _to_args_and_kwargs(self, tool_input: Union[str, Dict]) -> Tuple[Tuple, Dict]:
        return (), {}

    def _run(self):
        frame = take_photo()
        detected_objects = detect_objects(frame)
        cv2.imwrite("detected_image.jpg", frame)
        contexto = get_image_context("detected_image.jpg")
        return f"Puedo detectar: {detected_objects}, Contexto de la imagen: {contexto}"

    def _arun(self):
        raise NotImplementedError("photo_detection does not support async")
