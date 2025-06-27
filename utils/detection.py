import cv2
from ultralytics import YOLO

model = YOLO("InsulatorFaultDetectionProject/model/best.pt")

# === Updated function ===
def detect_fault_from_image(image_path):
    frame = cv2.imread(image_path)
    if frame is None:
        raise FileNotFoundError(f"Image not found: {image_path}")

    results = model(frame)[0]
    outputs = []
    for det in results.boxes:
        cls_id = int(det.cls.item())
        label = model.names[cls_id]
        conf = float(det.conf.item())
        xyxy = det.xyxy.tolist()[0]  # Bounding box
        outputs.append({"label": label, "confidence": conf, "bbox": xyxy})
    return outputs
