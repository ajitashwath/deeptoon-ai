from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import cv2
import numpy as np
import base64
import io
import os
from datetime import datetime
import uuid
from PIL import Image, ImageEnhance, ImageFilter
import skimage
from skimage import filters, segmentation, color

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
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur_value = blur_value if blur_value % 2 == 1 else blur_value + 1
        gray_blur = cv2.medianBlur(gray, blur_value)
        
        line_size = line_size if line_size % 2 == 1 else line_size + 1
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
        img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        height, width = img_bgr.shape[:2]
        if width > 1000:
            scale = 1000 / width
            new_width = int(width * scale)
            new_height = int(height * scale)
            img_bgr = cv2.resize(img_bgr, (new_width, new_height), interpolation = cv2.INTER_AREA)
        
        num_filters = min(max(cartoon_intensity, 1), 10) 
        smooth = self.bilateral_filter_stack(
            img_bgr, 
            num_filters = num_filters,
            d = 9,
            sigma_color = 200,
            sigma_space = 200
        )
        
        color_levels = max(4, min(color_levels, 32))  
        quantized = self.color_quantization(smooth, k=color_levels)
        
        edge_thickness = max(1, min(edge_thickness, 10))  
        line_size = 3 + edge_thickness * 2
        blur_value = 3 + edge_thickness
        
        line_size = max(3, line_size if line_size % 2 == 1 else line_size + 1)
        blur_value = max(3, blur_value if blur_value % 2 == 1 else blur_value + 1)
        edges = self.edge_mask(img_bgr, line_size, blur_value)
        
        edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        cartoon = cv2.bitwise_and(quantized, edges)
        
        # You can uncomment this for different effect:
        # edges_inv = cv2.bitwise_not(edges)
        # cartoon = cv2.bitwise_and(quantized, edges_inv)
        cartoon_rgb = cv2.cvtColor(cartoon, cv2.COLOR_BGR2RGB)
        return cartoon_rgb
    
class AdvancedFilters:    
    def __init__(self):
        pass
    
    def oil_painting_effect(self, img, radius = 7, levels = 20):
        if isinstance(img, Image.Image):
            img = np.array(img)

        oil_img = cv2.xphoto.oilPainting(img, radius, levels)
        return oil_img
    
    def watercolor_effect(self, img, sigma_s = 50, sigma_r = 0.4):
        if isinstance(img, Image.Image):
            img = np.array(img)
        smooth = cv2.edgePreservingFilter(img, flags = 1, sigma_s = sigma_s, sigma_r = sigma_r)
        watercolor = cv2.bilateralFilter(smooth, 15, 80, 80)
        return watercolor
    
    def pencil_sketch(self, img, sigma_s = 60, sigma_r = 0.07, shade_factor = 0.02):
        if isinstance(img, Image.Image):
            img = np.array(img)
        
        gray, colored = cv2.pencilSketch(img, sigma_s = sigma_s, sigma_r = sigma_r, shade_factor = shade_factor)
        return gray, colored
    
    def anime_style(self, img, num_downsamples = 2, num_bilateral = 7):
        if isinstance(img, Image.Image):
            img = np.array(img)
        
        height, width = img.shape[:2]
        for _ in range(num_downsamples):
            img = cv2.pyrDown(img)
        
        for _ in range(num_bilateral):
            img = cv2.bilateralFilter(img, 9, 200, 200)
        
        for _ in range(num_downsamples):
            img = cv2.pyrUp(img)
        
        img = cv2.resize(img, (width, height))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)
        edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        anime = cv2.bitwise_and(img, edges)
        return anime
    
    def pop_art_effect(self, img, k = 4):
        if isinstance(img, Image.Image):
            img = np.array(img)
        
        data = img.reshape((-1, 3)).astype(np.float32)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
        _, labels, centers = cv2.kmeans(data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        
        centers = np.uint8(centers)
        segmented_data = centers[labels.flatten()]
        pop_art = segmented_data.reshape(img.shape)
        
        # Increase saturation
        pop_art_pil = Image.fromarray(pop_art)
        enhancer = ImageEnhance.Color(pop_art_pil)
        pop_art_pil = enhancer.enhance(2.0) 
        return np.array(pop_art_pil)


converter = CartoonConverter()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods = ['POST'])
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
        cartoon_pil = Image.fromarray(cartoon_img.astype('uint8'))
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
        print(f"Error processing image: {str(e)}") 
        return jsonify({'success': False, 'error': str(e)})

@app.route('/download/<result_id>')
def download_result(result_id):
    try:
        result_path = os.path.join(RESULT_FOLDER, f'{result_id}.png')
        if os.path.exists(result_path):
            return send_file(
                result_path, 
                as_attachment=True, 
                download_name=f'cartoonized_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
            )
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug = True, host = '0.0.0.0', port = 5000)