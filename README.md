# DeepToon AI 

Transform your photos into stunning cartoon artwork using advanced computer vision techniques. DeepToon AI is a web-based application that applies sophisticated image processing algorithms to create cartoon-style images from regular photographs.

![DeepToon](https://i.ibb.co/9kC1Sw7Q/Screenshot-2025-06-29-212703.png)

## Features

- **Smart Cartoonization**: Advanced bilateral filtering and color quantization for realistic cartoon effects
- **Customizable Parameters**: Adjust cartoon intensity, edge thickness, and color levels in real-time
- **Drag & Drop Interface**: User-friendly web interface with drag-and-drop image upload
- **Multiple Output Options**: Download high-quality cartoonized images instantly
- **Responsive Design**: Works seamlessly on desktop and mobile devices

##  Quick Start

### Prerequisites

- Python 3.7 or higher
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ajitashwathr10/deeptoon-ai.git
   cd deeptoon-ai
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Open your browser**
   Navigate to `http://localhost:5000` to start using DeepToon AI

## Usage

1. **Upload an Image**: Click the upload area or drag and drop your image
2. **Adjust Settings**: 
   - **Cartoon Intensity** (1-10): Controls smoothing strength
   - **Edge Thickness** (1-10): Adjusts outline boldness
   - **Color Levels** (4-32): Sets color simplification level
3. **Process**: Click "Cartoonize" to transform your image
4. **Download**: Save your cartoonized artwork

## Technical Architecture

### Computer Vision Pipeline

DeepToon AI uses a sophisticated multi-stage image processing pipeline:

#### 1. **Bilateral Filtering Stack**
- Applies multiple layers of bilateral filtering
- Preserves edges while smoothing textures
- Configurable intensity for different cartoon styles

#### 2. **K-Means Color Quantization**
- Reduces color palette using clustering algorithms
- Creates posterized, cartoon-like color schemes
- Adjustable cluster count for fine-tuning

#### 3. **Adaptive Edge Detection**
- Uses adaptive thresholding for edge extraction
- Customizable edge thickness and blur parameters
- Combines with quantized colors for final output

### Technology Stack

- **Backend**: Flask (Python)
- **Computer Vision**: OpenCV, scikit-image
- **Image Processing**: PIL/Pillow, NumPy
- **Frontend**: HTML5, CSS3, JavaScript
- **File Handling**: Base64 encoding, UUID generation

## Project Structure

```
deeptoon-ai/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Main web interface
├── static/
│   ├── styles.css        # UI styling
│   └── script.js         # Frontend logic
├── uploads/              # Temporary uploads (auto-created)
├── results/              # Processed images (auto-created)
└── README.md            # This file
```

## Configuration Options

### Cartoon Intensity (1-10)
- **Low (1-3)**: Subtle smoothing, maintains photo realism
- **Medium (4-7)**: Balanced cartoon effect
- **High (8-10)**: Heavy stylization, anime-like appearance

### Edge Thickness (1-10)
- **Thin (1-3)**: Delicate outlines
- **Medium (4-7)**: Standard cartoon edges
- **Thick (8-10)**: Bold, comic book style

### Color Levels (4-32)
- **Few (4-8)**: Highly posterized, pop art style
- **Medium (9-16)**: Balanced color reduction
- **Many (17-32)**: Subtle color simplification

## Advanced Usage

### API Endpoints

#### POST `/upload`
Processes an uploaded image with cartoonization effects.

**Request Body:**
```json
{
  "image": "data:image/jpeg;base64,/9j/4AAQ...",
  "intensity": 5,
  "edge_thickness": 2,
  "color_levels": 8
}
```

**Response:**
```json
{
  "success": true,
  "result_image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
  "result_id": "uuid-string"
}
```

#### GET `/download/<result_id>`
Downloads the processed image file.

### Extending the Application

The codebase includes additional filters in the `AdvancedFilters` class:

- **Oil Painting Effect**: Creates oil painting-style artwork
- **Watercolor Effect**: Applies watercolor painting aesthetics
- **Pencil Sketch**: Generates pencil drawing effects
- **Anime Style**: Specialized anime/manga conversion
- **Pop Art Effect**: High-contrast, pop art styling

## Troubleshooting

### Common Issues

**"Module not found" errors**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Large image processing failures**
- Images are automatically resized if width > 1000px
- Maximum file size: 10MB
- Supported formats: JPEG, PNG, WebP, BMP

**Memory issues with large images**
- The app automatically optimizes image size
- Consider reducing image resolution before upload

### Performance Optimization

- **Image Size**: Optimal size is 800-1200px width
- **Processing Time**: Typically 2-5 seconds per image
- **Memory Usage**: ~100-200MB per concurrent user

## Contributing

We welcome contributions! Here's how to get started:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/deeptoon-ai.git

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt

# Run in development mode
export FLASK_ENV=development  # On Windows: set FLASK_ENV=development
python app.py
```

## 📋 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| Flask | 2.3.3 | Web framework |
| flask-cors | 4.0.0 | Cross-origin resource sharing |
| opencv-python | 4.8.1.78 | Computer vision operations |
| numpy | 1.24.3 | Numerical computing |
| Pillow | 10.0.1 | Image processing |

## Acknowledgments
- OpenCV community for computer vision tools
- Flask developers for the web framework
