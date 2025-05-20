from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import cv2
import numpy as np
import base64
import io
from PIL import Image
import os
from datetime import datetime
import uuid

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'results'
os.makedirs(UPLOAD_FOLDER, exist_ok = True)
os.makedirs(RESULT_FOLDER, exist_ok = True)

class CartoonConverter:
    def __init__(self):
        pass
    
    def edge_mask(self, img, line_size, blur_value):
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        gray_blur = cv2.medianBlur(gray, blur_value)
        edges = cv2.adaptiveThreshold(gray_blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, line_size, blur_value)
        return edges
    
    def color_quantization(self, img, k = 8):
        data = img.reshape((-1, 3))
        data = np.float32(data)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
        _, labels, centers = cv2.kmeans(data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        centers = np.uint8(centers)
        segmented_data = centers[labels.flatten()]
        segmented_image = segmented_data.reshape(img.shape)
        return segmented_image
    
    def bilateral_filter_stack(self, img, num_filters = 7, d = 9, sigma_color = 80, sigma_space = 80):
        filtered = img.copy()
        for _ in range(num_filters):
            filtered = cv2.bilateralFilter(filtered, d, sigma_color, sigma_space)
        return filtered
    
    def cartoonize(self, img, cartoon_intensity = 5, edge_thickness = 2, color_levels = 8):
        height, width = img.shape[:2]
        if width > 1000:
            scale = 1000 / width
            new_width = int(width * scale)
            new_height = int(height * scale)
            img = cv2.resize(img, (new_width, new_height), interpolation = cv2.INTER_AREA)
        
        num_filters = min(cartoon_intensity, 10)
        smooth = self.bilateral_filter_stack(img, num_filters = num_filters)
        
        quantized = self.color_quantization(smooth, k = color_levels)
        
        line_size = 5 + edge_thickness * 2
        blur_value = 5 + edge_thickness
        edges = self.edge_mask(img, line_size, blur_value)
        
        edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
        
        cartoon = cv2.bitwise_and(quantized, edges)
        return cartoon

converter = CartoonConverter()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        image_data = request.json['image']
        cartoon_intensity = int(request.json.get('intensity', 5))
        edge_thickness = int(request.json.get('edge_thickness', 2))
        color_levels = int(request.json.get('color_levels', 8))
        image_data = image_data.split(',')[1]  
        image_bytes = base64.b64decode(image_data)
        pil_image = Image.open(io.BytesIO(image_bytes))
        
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        img_array = np.array(pil_image)
        
        cartoon_img = converter.cartoonize(
            img_array, 
            cartoon_intensity = cartoon_intensity,
            edge_thickness = edge_thickness,
            color_levels = color_levels
        )
        cartoon_pil = Image.fromarray(cartoon_img)
    
        result_id = str(uuid.uuid4())
        result_path = os.path.join(RESULT_FOLDER, f'{result_id}.png')
        cartoon_pil.save(result_path)
    
        buffered = io.BytesIO()
        cartoon_pil.save(buffered, format = "PNG")
        cartoon_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        return jsonify({
            'success': True,
            'result_image': f'data:image/png;base64,{cartoon_base64}',
            'result_id': result_id
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/download/<result_id>')
def download_result(result_id):
    try:
        result_path = os.path.join(RESULT_FOLDER, f'{result_id}.png')
        if os.path.exists(result_path):
            return send_file(result_path, as_attachment = True, download_name = f'cartoonized_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug = True, host = '0.0.0.0', port = 5000)