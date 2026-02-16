# 🔒 Phishing Website Detection System

A machine learning-based phishing detection system that analyzes URLs and predicts whether they are legitimate or potentially malicious. The system extracts 30+ features from URLs and uses trained ML models to classify websites in real-time.


---

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Live Demo](#live-demo)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Testing with Sample URLs](#testing-with-sample-urls)
- [Project Structure](#project-structure)
- [Deployment](#deployment)
- [Model Training](#model-training)
- [Contributing](#contributing)
- [License](#license)

---

## ✨ Features

- **Real-time URL Analysis**: Instantly analyze any URL for phishing indicators
- **30+ Feature Extraction**: Comprehensive feature set including:
  - URL structure analysis (IP address, length, special characters)
  - Domain characteristics (age, DNS records, SSL certificate)
  - Content-based features (forms, external links, redirects)
  - Reputation metrics (Google index, page rank, web traffic)
- **RESTful API**: Easy-to-use JSON API for integration
- **Batch Processing**: Analyze multiple URLs simultaneously
- **Web Interface**: User-friendly UI for quick URL checks
- **Model Persistence**: Pre-trained models with MLflow tracking
- **Cloud Deployment**: Fully containerized and deployed on AWS

---

## 🏗️ Architecture

```
User Request → Flask API → Feature Extractor → ML Model → Prediction
                                                    ↓
                                            MongoDB (Training Data)
                                                    ↓
                                            DagsHub + MLflow (Model Tracking)
```

**Key Components:**
- **Flask Backend**: Handles HTTP requests and responses
- **URLFeatureExtractor**: Extracts 30 security-relevant features from URLs
- **NetworkModel**: Scikit-learn based classifier with preprocessing pipeline
- **MongoDB**: Stores training data and historical predictions
- **DagsHub**: Tracks experiments and model versions
- **Docker**: Containerization for consistent deployments
- **AWS ECR**: Docker image registry
- **AWS EC2**: Production hosting environment

---

## 🌐 Live Demo

**Access the live application:**

🔗 **Web Interface**: `http://50.19.16.94:8080`

🔗 **API Endpoint**: `http://50.19.16.94:8080/predict-url`

🔗 **Health Check**: `http://50.19.16.94:8080/health`

> ⚠️ **Note**: This is a development instance. The IP address may change if the EC2 instance is restarted. For production use, consider setting up an Elastic IP or domain name.

---

## 🛠️ Technology Stack

### Backend & ML
- **Python 3.10**: Core programming language
- **Flask**: Web framework for API
- **Scikit-learn**: Machine learning models
- **Pandas**: Data manipulation
- **NumPy**: Numerical computations

### Infrastructure
- **Docker**: Containerization
- **AWS EC2**: Cloud hosting
- **AWS ECR**: Container registry
- **GitHub Actions**: CI/CD pipeline

### MLOps
- **DagsHub**: Experiment tracking
- **MLflow**: Model versioning and registry
- **MongoDB**: Data storage

### DevOps
- **Git**: Version control
- **GitHub Actions**: Automated deployment
- **Self-hosted Runners**: Custom deployment agents

---

## 📥 Installation

### Prerequisites
- Python 3.10+
- Docker (optional, for containerized deployment)
- MongoDB instance
- AWS Account (for deployment)

### Local Setup

1. **Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/phishing-detection.git
cd phishing-detection
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**

Create a `.env` file in the project root:
```env
MONGODB_URL_KEY=your_mongodb_connection_string
DAGSHUB_USER_TOKEN=your_dagshub_token
```

5. **Run the application**
```bash
python App.py
```

The app will be available at `http://localhost:8080`

---

## 🚀 Usage

### Web Interface

1. Open your browser and navigate to `http://50.19.16.94:8080`
2. Enter the URL you want to check
3. Click "Check URL"
4. View the prediction result (Safe/Phishing/Suspicious)

### Using the API

#### Single URL Prediction

```bash
curl -X POST http://50.19.16.94:8080/predict-url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

**Response:**
```json
{
  "url": "https://example.com",
  "prediction": "Safe",
  "confidence": 95.67,
  "features": {
    "having_IP_Address": -1,
    "URL_Length": 1,
    "Shortining_Service": 1,
    ...
  }
}
```

#### Batch URL Prediction

```bash
curl -X POST http://50.19.16.94:8080/predict-batch \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      "https://google.com",
      "https://suspicious-site.tk",
      "http://192.168.1.1/login"
    ]
  }'
```

#### Health Check

```bash
curl http://50.19.16.94:8080/health
```

---

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web interface |
| `/predict-url` | POST | Predict single URL |
| `/predict-batch` | POST | Predict multiple URLs |
| `/predict` | POST | Upload CSV for batch prediction |
| `/train` | GET | Trigger model training |
| `/health` | GET | System health check |

### Request/Response Examples

#### `/predict-url` (POST)

**Request Body:**
```json
{
  "url": "https://example.com"
}
```

**Success Response (200):**
```json
{
  "url": "https://example.com",
  "prediction": "Safe",
  "confidence": 95.67,
  "features": {...}
}
```

**Error Response (500):**
```json
{
  "error": "Prediction failed",
  "message": "Connection timeout"
}
```

---

## 🧪 Testing with Sample URLs

### ✅ Safe/Legitimate URLs
Try these known safe websites:
```
https://www.google.com
https://www.github.com
https://www.wikipedia.org
https://www.amazon.com
https://www.microsoft.com
```

### ⚠️ Known Phishing URLs (Educational/Testing Only)

**IMPORTANT**: These URLs are provided for testing purposes only. They are known phishing sites that have been reported and may be inactive.

```
http://allegro-lokalnie.0f0f00f1-1.bond/
https://track.pstmrk.it/3s/africanfoodhelpsood77b9...
```

### 🔍 Additional Testing Resources

- **PhishTank**: https://phishtank.org/ - Database of verified phishing URLs
- **OpenPhish**: https://openphish.com/ - Active phishing feed
- **URLhaus**: https://urlhaus.abuse.ch/ - Malware URL database

### 🧪 Suspicious Patterns to Test

Create test URLs with these phishing characteristics:
```
http://paypal-verify-account.xyz
http://secure.login.verify.paypal.suspicious-domain.tk
http://192.168.1.1/login
http://google-login-secure.ml
```

> ⚠️ **Disclaimer**: Never enter personal information on suspicious websites. These URLs are for testing the detection system only.

---

## 📁 Project Structure

```
phishing-detection/
├── App.py                          # Main Flask application
├── Dockerfile                      # Docker configuration
├── requirements.txt                # Python dependencies
├── .github/
│   └── workflows/
│       └── main.yml               # CI/CD pipeline
├── Network_Security/
│   ├── Components/                # ML pipeline components
│   │   ├── Data_Ingestion.py
│   │   ├── Data_Validation.py
│   │   ├── Data_Transformation.py
│   │   └── Model_Trainer.py
│   ├── Pipelines/
│   │   ├── training_pipeline.py   # Training orchestration
│   │   └── prediction_pipeline.py # Inference orchestration
│   ├── Utils/
│   │   ├── main_utils/            # General utilities
│   │   ├── ml_utils/              # ML-specific utilities
│   │   └── extractor/
│   │       └── url_feature_extractor.py  # Feature extraction
│   ├── Exception_Handling/
│   ├── Logging/
│   └── Constants/
├── templates/
│   ├── index.html                 # Main UI
│   └── table.html                 # Results display
├── Final_Model/
│   ├── Preprocessor.pkl           # Trained preprocessor
│   └── Model.pkl                  # Trained ML model
├── data_schema/
│   └── schema_training.json       # Feature definitions
└── Prediction_Output/             # Prediction results
```

---

## 🚢 Deployment

### Docker Deployment

1. **Build the Docker image**
```bash
docker build -t phishing-detection .
```

2. **Run the container**
```bash
docker run -d \
  --name phishing-app \
  -p 8080:8080 \
  -e DAGSHUB_USER_TOKEN=your_token \
  phishing-detection
```

### AWS EC2 Deployment (Automated via GitHub Actions)

The project uses GitHub Actions for automated CI/CD:

**Workflow Steps:**
1. **Continuous Integration**: Linting and testing
2. **Build & Push**: Docker image built and pushed to AWS ECR
3. **Deploy**: Image pulled and deployed on EC2 instance

**Setup Requirements:**
1. AWS ECR repository created
2. EC2 instance with Docker installed
3. Self-hosted GitHub Actions runner on EC2
4. GitHub Secrets configured:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_REGION`
   - `ECR_REPOSITORY_NAME`
   - `AWS_ECR_LOGIN_URI`
   - `DAGSHUB_TOKEN`

**Deployment Trigger:**
```bash
git add .
git commit -m "Deploy updates"
git push origin main
```

The application will automatically build, test, and deploy to EC2.

---

## 🎓 Model Training

### Features Extracted (30 Total)

The system extracts these security-relevant features from each URL:

**URL-based Features (12)**
- `having_IP_Address`: URL contains IP address
- `URL_Length`: Length category (short/medium/long)
- `Shortining_Service`: Uses URL shortener (bit.ly, etc.)
- `having_At_Symbol`: Contains @ symbol
- `double_slash_redirecting`: Has // in path
- `Prefix_Suffix`: Uses dash in domain
- `having_Sub_Domain`: Number of subdomains
- `SSLfinal_State`: HTTPS certificate status
- `Domain_registeration_length`: Domain age
- `Favicon`: Favicon loaded from same domain
- `port`: Non-standard port usage
- `HTTPS_token`: HTTPS in domain name (suspicious)

**Content-based Features (11)**
- `Request_URL`: Percentage of external requests
- `URL_of_Anchor`: Percentage of suspicious anchors
- `Links_in_tags`: Suspicious link tags
- `SFH`: Server Form Handler behavior
- `Submitting_to_email`: Form submits to email
- `Abnormal_URL`: URL matches WHOIS data
- `Redirect`: Number of redirects
- `on_mouseover`: Status bar manipulation
- `RightClick`: Right-click disabled
- `popUpWidnow`: Contains popups
- `Iframe`: Uses invisible iframes

**Domain-based Features (7)**
- `age_of_domain`: Domain registration age
- `DNSRecord`: DNS record exists
- `web_traffic`: Alexa/traffic rank
- `Page_Rank`: Google PageRank
- `Google_Index`: Indexed by Google
- `Links_pointing_to_page`: Number of backlinks
- `Statistical_report`: IP in blacklists

### Training the Model

```bash
# Trigger training via API
curl http://50.19.16.94:8080/train

# Or run locally
python -c "from Network_Security.Pipelines.training_pipeline import TrainingPipeline; TrainingPipeline().run_pipeline()"
```

### Model Performance

- **Algorithm**: Random Forest / XGBoost (configurable)
- **Accuracy**: ~95%+ on test set
- **Features**: 30 engineered features
- **Training Data**: Sourced from PhishTank, OpenPhish, and legitimate sites

---

## 🔒 Security Considerations

### About Public IP Address

**Is it safe to share the public IP in README?**

✅ **Yes, with considerations:**
- The IP is already public-facing (accessible to anyone)
- Your security relies on proper AWS Security Group configuration, not IP secrecy
- However, consider these best practices:

**Recommended for Production:**
1. Use an **Elastic IP** (stays constant even if instance restarts)
2. Set up a **domain name** (looks more professional)
3. Add **HTTPS with SSL/TLS certificate** (Let's Encrypt is free)
4. Enable **AWS WAF** (Web Application Firewall)
5. Set up **CloudFront** for DDoS protection
6. Use **rate limiting** to prevent abuse

**Current Setup:**
- HTTP only (no HTTPS) - fine for demo/testing
- Accessible from anywhere (0.0.0.0/0)
- No authentication required

### Hardening Checklist

- [ ] Enable HTTPS with valid SSL certificate
- [ ] Add API authentication (API keys, OAuth)
- [ ] Implement rate limiting
- [ ] Set up monitoring and alerts
- [ ] Regular security updates
- [ ] Database access controls
- [ ] Input validation and sanitization
- [ ] CORS configuration

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide
- Add unit tests for new features
- Update documentation as needed
- Ensure CI/CD pipeline passes

---

## 📊 Performance & Monitoring

### System Requirements

**Minimum:**
- 2 CPU cores
- 4 GB RAM
- 20 GB storage

**Recommended:**
- 4 CPU cores
- 8 GB RAM
- 50 GB storage

### Monitoring Endpoints

- Health check: `GET /health`
- Logs: Check `docker logs mltest` on EC2

---

## 🐛 Troubleshooting

### Common Issues

**Issue**: "Model not loaded" error
- **Solution**: Ensure `Final_Model/` directory contains `Preprocessor.pkl` and `Model.pkl`

**Issue**: Timeout errors
- **Solution**: Check EC2 Security Group allows inbound traffic on port 8080

**Issue**: DagsHub authentication errors
- **Solution**: Set `DAGSHUB_USER_TOKEN` environment variable

**Issue**: Connection refused
- **Solution**: Verify Docker container is running: `docker ps`

### Debug Commands

```bash
# Check if container is running
docker ps

# View container logs
docker logs mltest

# Check last 50 log lines
docker logs --tail 50 mltest

# Follow logs in real-time
docker logs -f mltest

# Restart container
docker restart mltest
```

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Your Name** (Update this with your info)
- GitHub: [@Karamjodh](https://github.com/Karamjodh)
- DagsHub: [@Karamjodh](https://dagshub.com/Karamjodh)

---

## 🙏 Acknowledgments

- PhishTank for phishing URL datasets
- OpenPhish for real-time phishing feeds
- Scikit-learn community
- Flask framework developers
- AWS for cloud infrastructure

---

## 📧 Contact & Support

For questions, issues, or suggestions:
- Open an issue on GitHub
- Email: rattan5650@gmail.com

---

## 🔮 Future Enhancements

- [ ] Add HTTPS support
- [ ] Implement user authentication
- [ ] Create admin dashboard
- [ ] Add more ML models (ensemble methods)
- [ ] Real-time learning from user feedback
- [ ] Browser extension
- [ ] Mobile app
- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] Export reports (PDF, CSV)

---

**Last Updated**: February 2026

---

⭐ If you find this project useful, please consider giving it a star on GitHub!