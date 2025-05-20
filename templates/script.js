let currentImageData = null;
let resultId = null;

document.addEventListener('DOMContentLoaded', function () {
    setupEventListeners();
    updateSliderValues();
});

function setupEventListeners() {
    const fileInput = document.getElementById('fileInput');
    const uploadSection = document.getElementById('uploadSection');
    fileInput.addEventListener('change', handleFileSelect);

    uploadSection.addEventListener('click', () => fileInput.click());
    uploadSection.addEventListener('dragover', handleDragOver);
    uploadSection.addEventListener('dragleave', handleDragLeave);
    uploadSection.addEventListener('drop', handleDrop);

    ['intensitySlider', 'edgeSlider', 'colorSlider'].forEach(id => {
        document.getElementById(id).addEventListener('input', updateSliderValues);
    });
}

function updateSliderValues() {
    document.getElementById('intensityValue').textContent = document.getElementById('intensitySlider').value;
    document.getElementById('edgeValue').textContent = document.getElementById('edgeSlider').value;
    document.getElementById('colorValue').textContent = document.getElementById('colorSlider').value;
}

function handleDragOver(e) {
    e.preventDefault();
    document.getElementById('uploadSection').classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    document.getElementById('uploadSection').classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    document.getElementById('uploadSection').classList.remove('dragover');
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        handleFile(file);
    }
}

function handleFile(file) {
    if (!file.type.startsWith('image/')) {
        showMessage('Please select a valid image file.', 'error');
        return;
    }

    const reader = new FileReader();
    reader.onload = function (e) {
        currentImageData = e.target.result;
        document.getElementById('originalImage').src = currentImageData;
        document.getElementById('controls').style.display = 'block';
        document.getElementById('actionButtons').style.display = 'flex';
        document.getElementById('controls').classList.add('fade-in');
        document.getElementById('actionButtons').classList.add('fade-in');

        showMessage('Image loaded successfully! Adjust settings and click Cartoonize.', 'success');
    };
    reader.readAsDataURL(file);
}

async function processImage() {
    if (!currentImageData) {
        showMessage('Please select an image first.', 'error');
        return;
    }
    document.getElementById('loading').style.display = 'block';
    document.getElementById('processBtn').disabled = true;
    document.getElementById('results').style.display = 'none';

    try {
        const payload = {
            image: currentImageData,
            intensity: parseInt(document.getElementById('intensitySlider').value),
            edge_thickness: parseInt(document.getElementById('edgeSlider').value),
            color_levels: parseInt(document.getElementById('colorSlider').value)
        };

        const response = await fetch('/upload', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        });

        const result = await response.json();

        if (result.success) {
            document.getElementById('cartoonImage').src = result.result_image;
            resultId = result.result_id;

            document.getElementById('results').style.display = 'block';
            document.getElementById('results').classList.add('fade-in');

            showMessage('Cartoonization completed successfully!', 'success');
        } else {
            showMessage('Error: ' + result.error, 'error');
        }

    } catch (error) {
        console.error('Error:', error);
        showMessage('Failed to process image. Please try again.', 'error');
    } finally {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('processBtn').disabled = false;
    }
}

function downloadResult() {
    if (resultId) {
        const link = document.createElement('a');
        link.href = `/download/${resultId}`;
        link.download = `cartoonized_${Date.now()}.png`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        showMessage('Download started!', 'success');
    }
}

function resetAll() {
    currentImageData = null;
    resultId = null;
    document.getElementById('fileInput').value = '';
    document.getElementById('controls').style.display = 'none';
    document.getElementById('actionButtons').style.display = 'none';
    document.getElementById('results').style.display = 'none';
    document.getElementById('loading').style.display = 'none';
    document.getElementById('statusMessage').innerHTML = '';
    document.getElementById('intensitySlider').value = 5;
    document.getElementById('edgeSlider').value = 2;
    document.getElementById('colorSlider').value = 8;
    updateSliderValues();
}

function showMessage(message, type) {
    const statusDiv = document.getElementById('statusMessage');
    statusDiv.innerHTML = `<div class="status-message status-${type}">${message}</div>`;
    if (type === 'success') {
        setTimeout(() => {
            statusDiv.innerHTML = '';
        }, 3000);
    }
}