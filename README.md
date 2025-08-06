Крута команда
pip install -r requirements.txt

▶️ Як запустити локально
bash
pip install -r requirements.txt
python app.py

🐳 Як запустити в Docker
bash
docker build -t firebase-python-app .
docker run -p 8080:8080 firebase-python-app

☁️ Як деплоїти на Cloud Run
bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/firebase-python-app
gcloud run deploy firebase-python-app \
  --image gcr.io/YOUR_PROJECT_ID/firebase-python-app \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

  