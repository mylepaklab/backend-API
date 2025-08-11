Curl to test : 
curl -i -H "Origin: http://localhost:3000" "https://flask-api-ann-jxtsjymlfa-uc.a.run.app/translate_string?text_to_translate=I%20am%20Ann"

gcloud config set project original-spider-468713-d4

gcloud projects add-iam-policy-binding original-spider-468713-d4 --member=serviceAccount:939136731215@cloudbuild.gserviceaccount.com --role=roles/run.admin

gcloud projects add-iam-policy-binding original-spider-468713-d4 --member=serviceAccount:939136731215@cloudbuild.gserviceaccount.com --role=roles/storage.admin

gcloud projects add-iam-policy-binding original-spider-468713-d4 --member=serviceAccount:939136731215@cloudbuild.gserviceaccount.com --role=roles/iam.serviceAccountUser

gcloud projects add-iam-policy-binding original-spider-468713-d4 --member=serviceAccount:939136731215@cloudbuild.gserviceaccount.com --role=roles/cloudbuild.builds.editor

gcloud run deploy flask-api-ann --source . --region us-central1 --allow-unauthenticated //deployment of code changes to server

gcloud run services update-traffic flask-api-ann --to-revisions=0 //diable traffic


