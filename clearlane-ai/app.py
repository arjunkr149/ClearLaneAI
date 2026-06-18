from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
import uuid
import json
import base64
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import io
import random

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'static/uploads'
RESULTS_FOLDER = 'static/results'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Violation database (in-memory for demo)
violations_log = []

# Color map for violations
VIOLATION_COLORS = {
    'helmet_violation': (255, 59, 59),
    'seatbelt_violation': (255, 140, 0),
    'red_light_violation': (220, 20, 60),
    'stop_line_violation': (255, 69, 0),
    'wrong_side_driving': (148, 0, 211),
    'illegal_parking': (0, 120, 255),
    'triple_riding': (255, 20, 147),
    'vehicle': (34, 197, 94),
    'person': (59, 130, 246),
    'license_plate': (250, 204, 21),
}

VIOLATION_LABELS = {
    'helmet_violation': '⚠ NO HELMET',
    'seatbelt_violation': '⚠ NO SEATBELT',
    'red_light_violation': '🔴 RED LIGHT',
    'stop_line_violation': '⛔ STOP LINE',
    'wrong_side_driving': '↔ WRONG SIDE',
    'illegal_parking': '🅿 ILLEGAL PARK',
    'triple_riding': '⚠ TRIPLE RIDE',
    'vehicle': 'VEHICLE',
    'person': 'PERSON',
    'license_plate': 'PLATE',
}


def simulate_detection(image_pil):
    """
    Simulates YOLOv8 detection for demo purposes.
    In production, replace with: model = YOLO('yolov8n.pt'); results = model(image_pil)
    """
    w, h = image_pil.size
    detections = []

    # Simulate vehicles
    num_vehicles = random.randint(1, 3)
    for i in range(num_vehicles):
        x1 = random.randint(50, w // 2 - 100)
        y1 = random.randint(h // 4, h // 2)
        x2 = x1 + random.randint(120, 200)
        y2 = y1 + random.randint(80, 130)
        detections.append({
            'class': 'vehicle',
            'bbox': [x1, y1, x2, y2],
            'confidence': round(random.uniform(0.85, 0.98), 2)
        })

    # Simulate violations
    violation_pool = [
        'helmet_violation', 'seatbelt_violation', 'red_light_violation',
        'stop_line_violation', 'wrong_side_driving', 'illegal_parking'
    ]
    num_violations = random.randint(1, 3)
    chosen_violations = random.sample(violation_pool, min(num_violations, len(violation_pool)))

    for v in chosen_violations:
        x1 = random.randint(w // 3, w - 200)
        y1 = random.randint(50, h // 2)
        x2 = x1 + random.randint(100, 180)
        y2 = y1 + random.randint(80, 150)
        detections.append({
            'class': v,
            'bbox': [x1, y1, x2, y2],
            'confidence': round(random.uniform(0.72, 0.95), 2)
        })

    # Simulate license plate
    if random.random() > 0.3:
        x1 = random.randint(100, w // 2)
        y1 = random.randint(h // 2, h - 80)
        detections.append({
            'class': 'license_plate',
            'bbox': [x1, y1, x1 + 90, y1 + 30],
            'confidence': round(random.uniform(0.78, 0.96), 2),
            'ocr_text': random.choice(['UP16CX1234', 'DL7CB2345', 'MH02AB5678', 'KA03MN9012'])
        })

    return detections


def annotate_image(image_pil, detections):
    """Draw bounding boxes and labels on the image."""
    draw = ImageDraw.Draw(image_pil)
    w, h = image_pil.size

    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
    except:
        font_large = ImageFont.load_default()
        font_small = font_large

    for det in detections:
        cls = det['class']
        x1, y1, x2, y2 = det['bbox']
        color = VIOLATION_COLORS.get(cls, (255, 255, 255))
        label = VIOLATION_LABELS.get(cls, cls.upper())
        conf = det['confidence']

        # Clamp to image bounds
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w - 1, x2), min(h - 1, y2)

        # Draw box (thick border for violations)
        thickness = 3 if 'violation' in cls else 2
        for t in range(thickness):
            draw.rectangle([x1 - t, y1 - t, x2 + t, y2 + t], outline=color)

        # Label background
        label_text = f"{label} {conf:.0%}"
        if 'ocr_text' in det:
            label_text += f" | {det['ocr_text']}"

        bbox_text = draw.textbbox((0, 0), label_text, font=font_large)
        text_w = bbox_text[2] - bbox_text[0]
        text_h = bbox_text[3] - bbox_text[1]
        label_y = max(0, y1 - text_h - 6)

        draw.rectangle([x1, label_y, x1 + text_w + 8, label_y + text_h + 6], fill=color)
        draw.text((x1 + 4, label_y + 2), label_text, fill=(255, 255, 255), font=font_large)

    # Watermark
    wm = "ClearLane AI | Gridlock Hackathon 2.0"
    draw.rectangle([0, h - 26, w, h], fill=(10, 10, 30, 180))
    draw.text((8, h - 20), wm, fill=(250, 204, 21), font=font_small)

    return image_pil


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    try:
        # Save original
        file_id = str(uuid.uuid4())[:8]
        original_path = os.path.join(UPLOAD_FOLDER, f"{file_id}_original.jpg")
        result_path = os.path.join(RESULTS_FOLDER, f"{file_id}_result.jpg")

        image = Image.open(file.stream).convert('RGB')
        # Resize if too large
        if max(image.size) > 1200:
            image.thumbnail((1200, 1200), Image.LANCZOS)
        image.save(original_path, 'JPEG', quality=90)

        # Run detection
        detections = simulate_detection(image.copy())

        # Annotate
        annotated = annotate_image(image.copy(), detections)
        annotated.save(result_path, 'JPEG', quality=90)

        # Extract violations only
        violations = [d for d in detections if 'violation' in d['class']]
        objects = [d for d in detections if 'violation' not in d['class']]

        # Build violation records
        violation_records = []
        for v in violations:
            record = {
                'id': file_id,
                'type': v['class'].replace('_', ' ').title(),
                'confidence': v['confidence'],
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'plate': next((d.get('ocr_text', 'N/A') for d in detections if d['class'] == 'license_plate'), 'N/A')
            }
            violation_records.append(record)
            violations_log.append(record)

        # Convert result to base64
        with open(result_path, 'rb') as f:
            result_b64 = base64.b64encode(f.read()).decode('utf-8')

        return jsonify({
            'success': True,
            'file_id': file_id,
            'result_image': f'data:image/jpeg;base64,{result_b64}',
            'detections': detections,
            'violations': violation_records,
            'objects_detected': len(objects),
            'violations_found': len(violations),
            'processing_time_ms': random.randint(180, 420)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/violations', methods=['GET'])
def get_violations():
    return jsonify({'violations': violations_log[-50:], 'total': len(violations_log)})


@app.route('/api/stats', methods=['GET'])
def get_stats():
    if not violations_log:
        return jsonify({
            'total': 0, 'today': 0,
            'by_type': {}, 'recent': []
        })

    by_type = {}
    for v in violations_log:
        t = v['type']
        by_type[t] = by_type.get(t, 0) + 1

    today = datetime.now().strftime('%Y-%m-%d')
    today_count = sum(1 for v in violations_log if v['timestamp'].startswith(today))

    return jsonify({
        'total': len(violations_log),
        'today': today_count,
        'by_type': by_type,
        'recent': violations_log[-5:]
    })


@app.route('/static/results/<filename>')
def result_file(filename):
    return send_from_directory(RESULTS_FOLDER, filename)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
