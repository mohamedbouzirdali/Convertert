from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
import uuid

# Import the resume parsing functions from our module
from resume_parser import parse_pdf, parse_image, parse_pptx, parse_docx

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Swagger UI setup
SWAGGER_URL = '/swagger'
API_URL = '/swagger.yaml'
swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

@app.route('/swagger.yaml')
def swagger_file():
    try:
        with open('swagger.yaml', 'r') as f:
            return f.read(), 200, {'Content-Type': 'text/yaml'}
    except Exception as e:
        return str(e), 500

@app.route('/upload-resume', methods=['POST'])
def upload_resume():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    uploaded_file = request.files['file']
    filename = uploaded_file.filename.lower()
    resume_id = str(uuid.uuid4())

    try:
        # Determine the file type and call the appropriate parser
        if filename.endswith('.pdf'):
            parsed_data = parse_pdf(uploaded_file)
        elif filename.endswith(('.png', '.jpg', '.jpeg')):
            parsed_data = parse_image(uploaded_file)
        elif filename.endswith('.pptx'):
            parsed_data = parse_pptx(uploaded_file)
        elif filename.endswith('.docx'):
            parsed_data = parse_docx(uploaded_file)
        else:
            return jsonify({"error": "Unsupported file format"}), 400

        # Build the structured JSON response
        result_dict = {
            "id": resume_id,
            "name": parsed_data.get("name", "Unknown"),
            "email": parsed_data.get("email", "Unknown"),
            "phone": parsed_data.get("phone", "Unknown"),
            "linkedin": parsed_data.get("linkedin", "Unknown"),
            "address": parsed_data.get("address", "Unknown"),
            "education": parsed_data.get("education", "Not specified"),
            "skills": parsed_data.get("skills", "Not specified"),
            "experience": parsed_data.get("experience", "Not specified"),
            "languages": parsed_data.get("languages", "Not specified"),
            "dob": parsed_data.get("dob", "Unknown"),
            "certifications": parsed_data.get("certifications", "Not specified"),
            "tools": parsed_data.get("tools", "Not specified"),
            "summary": parsed_data.get("summary", "Not specified"),
            "interests": parsed_data.get("interests", "Not specified"),
            "courses_conferences": parsed_data.get("courses_conferences", "Not specified")
        }

        return jsonify(result_dict), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
