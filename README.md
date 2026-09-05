# cctv_survalliance


## Installation
```
Face-Verification-App Installation required python==3.10
and
then run
pip install -r requirements.txt
```

## Python Code to Run app:
Our main code of application name **streamlit_app.py**. To run this Code 
```
cd Face-Verification-App
streamlit run face_verification_app.py 
```
When run the main code **streamlit_app.py** it will open login window of Biometric verification app. To login in our application
we already built in the (username, password) in our database **cctv_database.db** table **user** to (admin,admin).

After sucessful login the welcome page open with dashboard , all the details of person entry or exit time, unique id , name and camera entry or exit.
at side bar there is three option 
" Dashboard, Add Person ,Remove Person & Search Person" 
