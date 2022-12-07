import streamlit as st
import mysql.connector
import pandas as pd
# 웹 대시보드 개발 라이브러리인 스트림릿은,
# main 함수가 있어야 한다.

@st.experimental_singleton
def init_connection():
    return mysql.connector.connect(**st.secrets["mysql"])

conn = init_connection()

# Perform query.
# Uses st.experimental_memo to only rerun when the query changes or after 10 min.
@st.experimental_memo(ttl=600)
def run_query(query):
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()


sql = "SELECT * FROM analysis_v3_label limit 2"
rows = run_query(sql)

# 컬럼명 임시 지정
df = pd.DataFrame(rows, columns=range(1,40,2))


st.write(df)
# st.table(df)

def main() :
    st.title('connect to DBddd')
    st.title(f'{len(rows)}')

if __name__ == '__main__' :
    main()