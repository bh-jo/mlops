import streamlit as st
import mysql.connector
import pandas as pd
import numpy as np
import time
import email, smtplib, ssl
from git import Repo
from datetime import datetime
from pprint import pprint
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.mime.application import MIMEApplication

# 웹 대시보드 개발 라이브러리인 스트림릿은,
# main 함수가 있어야 한다.

# DB connect
# @st.experimental_singleton
# @st.cache_data
def init_connection():
    return mysql.connector.connect(**st.secrets["mysql"])

conn = init_connection()

# Perform query.
# Uses st.experimental_memo to only rerun when the query changes or after 10 min.
# @st.experimental_memo()
def run_query(query):
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()

# @st.experimental_memo
# def convert_df(df):
#    return df.to_csv(index=False).encode('utf-8')

# @st.experimental_memo()
def onClick(query_list):
    #DB Table update
    for q in query_list:
        print("query ==> ", q)
        run_query(q)
        conn.commit()


def get_index(df):
    list = df.to_list()
    return list.index(1) # why 1? 1: 배포된모델, 0: 그외

# @st.cache (suppress_st_warning=True, allow_output_mutation=True)
def get_model_table():
    table_col = ["DTFULL","MODEL", "DEPLOY", "R", "PROB","NMAE"]

    # get database table
    sql1 = f"SELECT * FROM analysis_v3_201105_sample_copy order by DTFULL DESC"
    rows2 = run_query(sql1)
    df = pd.DataFrame(rows2, columns=table_col, index=None) # 한번 불러오고 나선 페이지 새로고침 해도 변경이 안됨

    old_index = get_index(df["DEPLOY"])
    st.dataframe(df,use_container_width=True)

    return df, old_index

def on_button_click():
    st.session_state.error_message = ''
    st.session_state.result_message = ''

    st.session_state.result_message = f"{st.session_state.latest_version} version 배포가 진행됩니다"

    q = f"update analysis_v3_201105_sample_copy set deploy=0 where model='{st.session_state.prd_version}'"
    q2 = f"update analysis_v3_201105_sample_copy set deploy=1 where model='{st.session_state.latest_version}'"
    onClick([q, q2])
    st.session_state.prd_version = st.session_state.latest_version
    print(st.session_state)

    # Devops 에 main branch 로컬폴더(최신모델) 배포, build pipeline 동작
    # git_push() ????
    # 실제 모델 배포가 진행되는 부분



    # 배포결과 메일로 수신
    send_email(
        sender="devbh27@gmail.com",
        password="ijnqtpgvndnligyp",
        receiver="bhjo@lsitc.com",
        smtp_server="smtp.gmail.com",
        smtp_port=587,
        email_message=f"새로운 버전의 모델이({st.session_state.latest_version}) 배포 되었습니다.",
        subject="모델 배포됨"
    )

    
   
def git_push():
    PATH_OF_GIT_REPO = 'deployment_test'  # make sure .git folder is properly configured
    COMMIT_MESSAGE = f'{datetime.today().strftime("%Y%m%d_%H%M%S")} comment from python script'

    try:
        repo = Repo(PATH_OF_GIT_REPO)
        repo.git.add("model.txt")
        # repo.git.add("fdfersdfvzs.txt", update=True)
        repo.index.commit(COMMIT_MESSAGE)
        origin = repo.remote(name='origin')
        origin.push()
        print("git push!")
    except:
        print('Some error occured while pushing the code') 

def main() :
    # devops 와 연결

    st.subheader('전체 모델 리스트')
    model_info = get_model_table()
    model_df = model_info[0]
    model_index = model_info[1]
    
    st.session_state.latest_version = model_df[model_df['MODEL']==model_df['MODEL'].max()]["MODEL"].values[0]
    st.session_state.prd_version = model_df[model_df['DEPLOY']==1]["MODEL"].values[0]

    # 최신모델==운영모델 여부에 따른 레이아웃 변경
    if st.session_state.latest_version == st.session_state.prd_version:
        st.subheader('최신 모델이 배포되어 있습니다')
    else:
        # 레이아웃 나누기
        col1,col2 = st.columns(2)
        # col1,col2 = st.columns([2,3]) # 2:3 비율

        with col1 :
            st.subheader('최신 모델')
            st.table(model_df[model_df['MODEL']==st.session_state.latest_version].transpose())
            print("최신 버전 : ", st.session_state.latest_version)
            

        with col2 :
            st.subheader('현재 배포된 모델')
            st.table(model_df[model_df['DEPLOY']==1].transpose())
            print("운영 버전 : ", st.session_state.prd_version)

        checkbox = st.checkbox('최신 모델 배포')
        st.button('확인', key='confirm_btn', disabled=(checkbox is False), on_click=on_button_click)

        con = st.container()
        con.caption("Result")
        # if 'error_message' in st.session_state and st.session_state.error_message:
        #     con.error(st.session_state.error_message)
        if 'result_message' in st.session_state and st.session_state.result_message:
            con.write(st.session_state.result_message)

    print(st.session_state)

    # Form 을 사용하여 메일쓰기
    # 현재 시나리오에선 필요하지 않음

    # with st.form("email form"):
    #     subject = st.text_input(label="subject", placeholder="11")
    #     fullName = st.text_input(label="fullName", placeholder="22")
    #     email = st.text_input(label="email address", placeholder="33")
    #     text = st.text_area(label="text", placeholder="44")
    #     upload_file = st.file_uploader("attachment")
    #     submit_res = st.form_submit_button(label="send")

    #     if submit_res:
    #         extra_info = """
    #            ----------------------------
    #             Email address of sender {}\n
    #             Sender full name {}\n
    #            ----------------------------\n \n
    #         """.format(email, fullName)

    #         message = extra_info + text

    #         send_email(
    #             sender="devbh27@gmail.com",
    #             password="ijnqtpgvndnligyp",
    #             receiver="bhjo@lsitc.com",
    #             smtp_server="smtp.gmail.com",
    #             smtp_port=587,
    #             email_message=message,
    #             subject=subject,
    #             attachment=upload_file
    #         )

    # 그래프
    # y_lists=['PROB', 'NMAE', 'R', 'DEPLOY']
    # y_list = st.radio("y축 항목 선택", y_lists,horizontal=True)
    # st.line_chart(df, x='DTFULL', y=y_list)

    
    # 모델 배포 버튼
    # 리포트 DB에 배포된 버전 표시 필요함

def send_email(sender, password, receiver, smtp_server, smtp_port, email_message, subject, attachment=None):
    message = MIMEMultipart()
    message['To'] = Header(receiver)
    message['From']  = Header(sender)
    message['Subject'] = Header(subject)
    message.attach(MIMEText(email_message,'plain', 'utf-8'))
    if attachment:
        att = MIMEApplication(attachment.read(), _subtype="txt")
        att.add_header('Content-Disposition', 'attachment', filename=attachment.name)
        message.attach(att)

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.ehlo()
    server.login(sender, password)
    text = message.as_string()
    server.sendmail(sender, receiver, text)
    server.quit()

if __name__ == '__main__' :
    print("\ncall main()")
    main()
    


# csv = convert_df(df)

# # save csv button
# st.download_button(
#     "Press to Download",
#     csv,
#     "file.csv",
#     "text/csv",
#     key='download-csv'
# )
