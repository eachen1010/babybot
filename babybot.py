import streamlit as st
import numpy as np
import time
import requests
from send_email import send_email
import time


THRESHOLD_QUIET = 0
THRESHOLD_FUSSY = 20
THRESHOLD_AGITATED = 30
THRESHOLD_DISTRESSED = 40
EMAIL_TIME_GAP = 60

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

    print(st.session_state['temperatures'])
    print(st.session_state['humidities'])


    return st.session_state['temperatures'], st.session_state['humidities']


def main():
    st.title("BabyBot Dashboard")


    # Initializing session state
    if 'vitality' not in st.session_state:
        st.session_state['vitality'] = 'Alive'
    if 'decibels' not in st.session_state:
        st.session_state['decibels'] = np.random.randint(0, 10, size=5)
    if 'temperatures' not in st.session_state:
        st.session_state['temperatures'] = np.random.randint(-20, 41, size=5)
    if 'humidities' not in st.session_state:
        st.session_state['humidities'] = np.random.randint(-20, 41, size=5)
    if 'last_sent_hot_email' not in st.session_state:
        st.session_state['last_sent_hot_email'] = time.time()
    if 'last_sent_cry_email' not in st.session_state:
        st.session_state['last_sent_cry_email'] = time.time()
    if 'start_time' not in st.session_state:
        st.session_state['start_time'] = time.time()
    if 'reciever_email' not in st.session_state:
        st.session_state['reciever_email'] = ""

    
        
    if st.session_state['reciever_email']:
        st.session_state['temp'] = st.session_state['temperatures'][-1]
        st.session_state['humidity'] = st.session_state['humidities'][-1]

        
        end_time = time.time()
        elapsed_time = end_time - st.session_state['start_time']


        if len(st.session_state['decibels']) > 5:
            # Calculate the average of the last 5 elements
            average = np.mean(st.session_state['decibels'][-5:])
        else:
            average = np.mean(st.session_state['decibels'])


        if average < THRESHOLD_QUIET:
            st.session_state['baby_state'] = 'Quiet'
        elif average < THRESHOLD_FUSSY:
            st.session_state['baby_state'] = 'Fussy'
        elif average < THRESHOLD_AGITATED:
            st.session_state['baby_state'] = 'Agitated'
        elif average < THRESHOLD_DISTRESSED:
            st.session_state['baby_state'] = 'Distressed'
        print(time.time() - st.session_state['last_sent_hot_email'])
        if st.session_state['temperatures'][-1] > 30 and time.time() - st.session_state['last_sent_cry_email'] >= EMAIL_TIME_GAP:
            st.toast('Too hot!', icon='🔥')
            st.session_state['last_sent_hot_email'] = time.time()
            message = '''We've detected some higher temperatures in baby's room.\nIt might be getting a bit warm in there.\nPlease keep an eye on the temperature and make sure baby stays cool and comfortable.'''
            send_email('[URGENT] Baby May Overheat', message, st.session_state['reciever_email'])

        print(time.time() - st.session_state['last_sent_cry_email'])
        # if baby is distressed
        if average > 45 and time.time() - st.session_state['last_sent_cry_email'] >= EMAIL_TIME_GAP:
            st.toast('Baby Distressed!', icon='❗')
            st.session_state['last_sent_cry_email'] = time.time()
            message = '''We've noticed that baby's cries have become increasingly frequent and intense. It's possible that the baby may be experiencing discomfort or distress.\nPlease check on the baby immediately to ensure their well-being. If the situation persists, please consult with a pediatrician or seek medical attention.\nWe'll continue to monitor the situation and provide updates as needed.'''
            send_email('[URGENT] Baby Distressed', message, st.session_state['reciever_email'])

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
            st.code(st.session_state['baby_state'], language='python')
            st.markdown("**Baby Status:**")
            st.code(st.session_state['vitality'], language='python')
            st.markdown("**Notification Email:**")
            st.code(st.session_state['reciever_email'], language='python')

        # Add a new random temperature
        st.session_state['temperatures'] = np.append(st.session_state['temperatures'], np.random.randint(-20, 41))
        st.session_state['humidities'] = np.append(st.session_state['humidities'], np.random.randint(-20, 41))

        if elapsed_time < 5:
            st.session_state['decibels'] = np.append(st.session_state['decibels'], np.random.randint(0, 20))
        elif elapsed_time < 15:
            st.session_state['decibels'] = np.append(st.session_state['decibels'], np.random.randint(20, 30))
        elif elapsed_time < 20:
            st.session_state['decibels'] = np.append(st.session_state['decibels'], np.random.randint(30, 40))
        else:
            st.session_state['decibels'] = np.append(st.session_state['decibels'], np.random.randint(40, 50))

    else:
        reciever_email = st.text_input("Enter email to notify: ", "someone@mail.com")
        if not reciever_email == "someone@mail.com":
            st.session_state['reciever_email'] = reciever_email
    print(st.session_state['reciever_email'])
    time.sleep(3)
    st.rerun()

if __name__ == "__main__":
    
    main()