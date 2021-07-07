# vaani-survey
An online survey development app that helps design robust Audio Surveys and Execute them

```bash
git clone https://github.com/ICTD-IITD/Voice_App_Custom_Entity_Extraction.git
cd Voice_App_Custom_Entity_Extraction
virtualenv -p /usr/bin/python3.6 survey_env
source survey_env/bin/activate
cd voice_survey_android_app/voicebotserver
sudo apt install libpq-dev python3-dev
sudo apt-get install python-numpy libicu-dev
pip install -r requirements.txt
pip install pyicu
polyglot download embeddings2.hi
polyglot download ner2.hi
cd Name/libsvm-3.23/
rm svm-scale svm-train svm-predict svm.o
make
cd python/
make
python manage.py runserver
```

Use psql to create a database and follow the following blog:
- https://www.digitalocean.com/community/tutorials/how-to-use-postgresql-with-your-django-application-on-ubuntu-14-04
- Then make the same changes in settings.py

In Apache:
- Move the polyglot embeddings folder inside the /var/www/ folder
- Make sure the media folder has the permission to be read by Apache - chmod 777 will work 
- Also make sure that the phone is using Google's text to speech and not internal STT

- ssh -i vsurvey_ec2_creds.pem ubuntu@ec2-54-146-209-111.compute-1.amazonaws.com
