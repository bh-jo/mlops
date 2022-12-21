import streamlit as st
import mysql.connector
import pandas as pd

import email, smtplib, ssl

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# 웹 대시보드 개발 라이브러리인 스트림릿은,
# main 함수가 있어야 한다.

@st.experimental_singleton
def init_connection():
    return mysql.connector.connect(**st.secrets["mysql"])

# conn = init_connection()

# Perform query.
# Uses st.experimental_memo to only rerun when the query changes or after 10 min.
# @st.experimental_memo
# def run_query(query):
#     with conn.cursor() as cur:
#         cur.execute(query)
#         return cur.fetchall()


# sql = "SELECT * FROM analysis_v3_label limit 2"
# rows = run_query(sql)

# 컬럼명 임시 지정
# df = pd.DataFrame(rows, columns=range(1,40,2))


# st.write(df)
# st.table(df)

def main() :
    # print DB table
    # st.title('connect to DB')
    # st.title(f'{len(rows)}')

    # select box
    select_list = ['10.1', '10.2', '10.3']
    option = st.selectbox('Please select in selectbox!', select_list)
	
    st.write('You selected:', option)

    # send email
    subject = "An email with attachment from Python"
    body = "This is an email with attachment sent from Python"
    sender_email = "bhjo@lsitc.com"
    receiver_email = "bhjo@lsitc.com"
    password = input("Type your password and press enter:")

    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message["Bcc"] = receiver_email  # Recommended for mass emails

    # Add body to email
    message.attach(MIMEText(body, "plain"))

    filename = "Aggregate.pdf"  # In same directory as script

    # Open PDF file in binary mode
    with open(filename, "rb") as attachment:
        # Add file as application/octet-stream
        # Email client can usually download this automatically as attachment
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    # Encode file in ASCII characters to send by email    
    encoders.encode_base64(part)

    # Add header as key/value pair to attachment part
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename}",
    )

    # Add attachment to message and convert message to string
    message.attach(part)
    text = message.as_string()

    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)

if __name__ == '__main__' :
    main()

