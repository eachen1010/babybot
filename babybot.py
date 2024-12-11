import streamlit as st
import numpy as np
import time
from send_email import send_email
import time
import pymongo
from db_get import BabyStats


THRESHOLD_QUIET = 0
THRESHOLD_FUSSY = 20
THRESHOLD_AGITATED = 30
THRESHOLD_DISTRESSED = 40
EMAIL_TIME_GAP = 120
DB_PASSWORD = '55jYmZd9jScKXhrU'

# Connect to MongoDB database
client = pymongo.MongoClient(f'mongodb+srv://eachen1010:{DB_PASSWORD}@babybotdb.ioh3s.mongodb.net/') # Replace with your connection string
db = client["baby_stats"]
collection = db["babybot_stats"]

@st.cache_data
def gather_data():
    # Initialize temperatures if not present in session state
    if 'temperatures' not in st.session_state:
        st.session_state['temperatures'] = np.random.randint(-20, 41, size=5)
    if 'humidity' not in st.session_state:
        st.session_state['humidities'] = np.random.randint(-20, 41, size=5)

    # Add a new random temperature
    st.session_state['temperatures'] = np.append(st.session_state['temperatures'], np.random.randint(-20, 41))
    st.session_state['humidities'] = np.append(st.session_state['humidities'], np.random.randint(-20, 41))

    return st.session_state['temperatures'], st.session_state['humidities']

# Check if the temperature is too hot or cold.
# Send an email if appropriate.
def check_temperature():
    print(time.time() - st.session_state['last_sent_email'])
    # Check if the baby is overheating 
    if st.session_state['temperatures'][-1] > 25 and time.time() - st.session_state['last_sent_email'] >= EMAIL_TIME_GAP:
        st.toast('Too hot!', icon='⚠️')
        st.session_state['last_sent_email'] = time.time()
        message = '''We've detected some higher temperatures in baby's room.\nIt might be getting a bit warm in there.\nPlease keep an eye on the temperature and make sure baby stays cool and comfortable.'''
        send_email('[URGENT] Baby May Overheat', message, st.session_state['reciever_email'])

    # Check if the baby is too cold.
    if st.session_state['temperatures'][-1] > 18 and time.time() - st.session_state['last_sent_email'] >= EMAIL_TIME_GAP:
        st.toast('Too cold!', icon='⚠️')
        st.session_state['last_sent_email'] = time.time()
        message = '''We've detected some lower temperatures in baby's room.\nIt might be getting a bit cold in there.\nPlease keep an eye on the temperature and make sure baby stays warm and comfortable.'''
        send_email('[URGENT] Baby May Be Cold', message, st.session_state['reciever_email'])


# Check if the room is too humid or too dry.
# Send an email if appropriate.
def check_humidity():
    # Check if too humid
    if st.session_state['humidities'][-1] > 55 and time.time() - st.session_state['last_sent_email'] >= EMAIL_TIME_GAP:
        st.toast('Too humid!', icon='⚠️')
        st.session_state['last_sent_email'] = time.time()
        message = '''We've detected higher humidity in baby's room.\nIt might be getting a bit humid in there.\nPlease keep an eye on the humidity and make sure baby stays comfortable.'''
        send_email('[URGENT] Humid Environment Warning', message, st.session_state['reciever_email'])

    # Check if too dry.
    if st.session_state['humidities'][-1] < 30 and time.time() - st.session_state['last_sent_email'] >= EMAIL_TIME_GAP:
        st.toast('Too dry!', icon='⚠️')
        st.session_state['last_sent_email'] = time.time()
        message = '''We've detected very low humidity in baby's room.\nIt might be getting a bit dry in there.\nPlease keep an eye on the humidity and make sure baby stays comfortable.'''
        send_email('[URGENT] Dry Environment Warning', message, st.session_state['reciever_email'])


# Check if the baby is quiet, fussy, agitated, or distressed.
# Send an email accordingly.
def check_volume():
    # if baby is distressed
    if st.session_state['states'][-1] == "D" and time.time() - st.session_state['last_sent_email'] >= EMAIL_TIME_GAP:
        st.toast('Baby Distressed!', icon='❗')
        st.session_state['last_sent_email'] = time.time()
        message = '''We've noticed that baby's cries have become increasingly frequent and intense. It's possible that the baby may be experiencing discomfort or distress.\nPlease check on the baby immediately to ensure their well-being. If the situation persists, please consult with a pediatrician or seek medical attention.\nWe'll continue to monitor the situation and provide updates as needed.'''
        send_email('[URGENT] Baby Distressed', message, st.session_state['reciever_email'])

def main():
    st.title("BabyBot Dashboard")

    # Initializing session state
    if 'db_client' not in st.session_state:
        st.session_state['db_client'] = BabyStats(DB_PASSWORD=DB_PASSWORD)
    if 'decibels' not in st.session_state and 'temperatures' not in st.session_state and 'humidities' not in st.session_state and 'states' not in st.session_state:
        st.session_state['temperatures'], st.session_state['humidities'], st.session_state['decibels'], st.session_state['states'] = st.session_state['db_client'].update_arrays()
    if 'last_sent_email' not in st.session_state:
        st.session_state['last_sent_email'] = time.time() - EMAIL_TIME_GAP
    if 'start_time' not in st.session_state:
        st.session_state['start_time'] = time.time()
    if 'reciever_email' not in st.session_state:
        st.session_state['reciever_email'] = ""

        
    if st.session_state['reciever_email']:
        st.session_state['temp'] = st.session_state['temperatures'][-1]
        st.session_state['humidity'] = st.session_state['humidities'][-1]
        check_humidity()
        check_temperature()
        check_volume()
        
        end_time = time.time()
        elapsed_time = end_time - st.session_state['start_time']


        col1, col2 = st.columns(2)

        with col1: 
            st.line_chart(st.session_state['temperatures'], x_label='Time', y_label="Temperature")
            st.line_chart(st.session_state['decibels'], x_label='Time', y_label="Decibels")
        
        with col2:
            st.line_chart(st.session_state['humidities'], x_label='Time', y_label="Humidity")

        # Sidebar for input features
        with st.sidebar:
            st.subheader("Current Stats")
            st.markdown("**Temperature:**")
            st.code(st.session_state['temp'], language='python')
            st.markdown("**Humidity:**")
            st.code(st.session_state['humidity'], language='python')
            st.markdown("**Baby State:**")
            if st.session_state['states'][-1] == "Q":
                st.code("QUIET", language='python')
            elif st.session_state['states'][-1] == "F":
                st.code("FUSSY", language='python')
            elif st.session_state['states'][-1] == "A":
                st.code("AGITATED", language='python')
            else:
                st.code("DISTRESSED", language='python')
            st.markdown("**Notification Email:**")
            st.code(st.session_state['reciever_email'], language='python')

        st.session_state['temperatures'], st.session_state['humidities'], st.session_state['decibels'], st.session_state['states'] = st.session_state['db_client'].update_arrays()

    else:
        reciever_email = st.text_input("Enter email to notify: ", "eachen1010@gmail.com")
        if not reciever_email == "someone@mail.com":
            st.session_state['reciever_email'] = reciever_email

    time.sleep(3)
    st.rerun()

if __name__ == "__main__":
    
    main()