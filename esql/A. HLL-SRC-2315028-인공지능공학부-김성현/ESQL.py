import mysql.connector
from datetime import datetime

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="khyun0303",
        database="ESQL"
    )


def create_schema():
    schema_creation_query = """
CREATE TABLE 사용자 (
	사용자_ID INT PRIMARY KEY,
    이름 VARCHAR(50) NOT NULL,
    성별 CHAR(1) CHECK (성별 IN ('M','F')),
    연락처 VARCHAR(15) NOT NULL,
    주민번호 CHAR(15) UNIQUE NOT NULL
);

CREATE TABLE 계좌 (
	계좌번호 INT PRIMARY KEY, 
    사용자_ID INT,
    계좌유형 VARCHAR(20) CHECK(계좌유형 IN ('저축','당좌','정기예금')),
    잔액 DECIMAL(15, 2) DEFAULT 0,
    FOREIGN KEY (사용자_ID) REFERENCES 사용자(사용자_ID)
);

CREATE TABLE 거래내역 (
	거래_ID INT PRIMARY KEY, 
    계좌번호 INT,
    거래일시 TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    거래유형 VARCHAR(10) CHECK (거래유형 IN ('입금','출금')),
    거래금액 DECIMAL(15, 2) REFERENCES 계좌(계좌번호)
);

CREATE TABLE 지점 (
	지점_ID INT PRIMARY KEY,
    위치 VARCHAR(100) NOT NULL,
    지점장_이름 VARCHAR(50) NOT NULL,
    직원수 INT CHECK (직원수 >= 0)
);
    """
    try:
        connection = connect_db()
        if connection is None:
            print("데이터베이스와 연결이 안됩니다.")

        cursor = connection.cursor()
        cursor.execute(schema_creation_query, multi=True)
        connection.commit()
        print("데이터베이스가 성공적으로 만들어졌습니다.")

    except mysql.connector.Error as e:
        if "already exists" in str(e):
            print("\n 데이터베이스가 이미 존재합니다.")
        else:
            print(f"Unexpected error occurred: {e}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# 사용자 정보 조회 함수
def get_user_info(user_id):
    db = connect_db()
    cursor = db.cursor()
    query = """
    SELECT 사용자.이름, 사용자.성별, 사용자.연락처, 계좌.계좌번호
    FROM 사용자
    JOIN 계좌 ON 사용자.사용자_ID = 계좌.사용자_ID
    WHERE 사용자.사용자_ID = %s;
    """
    print("\n---------------SQL Code Test---------------\n", query)
    print("---------------------------------------------\n")
    cursor.execute(query, (user_id,))
    result = cursor.fetchall()
    db.close()
    return result

# 사용자 거래내역 조회 함수
def get_account_history(account_number):
    db = connect_db()
    cursor = db.cursor()
    query = """
    SELECT 사용자.이름, 거래내역.거래일시, 거래내역.거래유형, 거래내역.거래금액, 지점.위치
    FROM 거래내역
    JOIN 계좌 ON 거래내역.계좌번호 = 계좌.계좌번호
    JOIN 사용자 ON 계좌.사용자_ID = 사용자.사용자_ID
    JOIN 지점 ON 사용자.지점_ID = 지점.지점_ID
    WHERE 계좌.계좌번호 = %s;
    """
    print("\n---------------SQL Code Test---------------\n", query)
    print("---------------------------------------------\n")
    cursor.execute(query, (account_number,))
    result = cursor.fetchall()
    db.close()
    return result

# 계좌 잔액 조회 함수 (출금을 위한 확인용)
def get_account_balance(account_number):
    db = connect_db()
    cursor = db.cursor()
    query = "SELECT 잔액 FROM 계좌 WHERE 계좌번호 = %s;"
    print("\n---------------SQL Code Test---------------\n", query)
    print("---------------------------------------------\n")
    cursor.execute(query, (account_number,))
    result = cursor.fetchone()
    db.close()
    return result[0] if result else None

from datetime import datetime

#잔액 업데이트 함수
def update_account(account_number, amount, transaction_type):
    db = connect_db()
    cursor = db.cursor()
    if transaction_type == "입금":
        update_query = "UPDATE 계좌 SET 잔액 = 잔액 + %s WHERE 계좌번호 = %s;"
        print("\n---------------SQL Code Test---------------\n", update_query)
        print("---------------------------------------------\n")
    elif transaction_type == "출금":
        update_query = "UPDATE 계좌 SET 잔액 = 잔액 - %s WHERE 계좌번호 = %s;"
        print("\n---------------SQL Code Test---------------\n", update_query)
        print("---------------------------------------------\n")
    cursor.execute(update_query, (amount, account_number))
    
    query = "SELECT COALESCE(MAX(거래_ID), 2000) + 1 AS next_transaction_id FROM 거래내역;"
    print("\n----------------SQL Code Test--------------\n", query)
    print("---------------------------------------------\n")
    cursor.execute(query)
    
    transaction_id_result = cursor.fetchone()
    if transaction_id_result and transaction_id_result[0] is not None:
        transaction_id = transaction_id_result[0]
    else:
        transaction_id = 2001 

    insert_query = """
    INSERT INTO 거래내역 (거래_ID, 계좌번호, 거래일시, 거래유형, 거래금액)
    VALUES (%s, %s, %s, %s, %s);
    """
    print("\n----------------SQL Code Test--------------\n, insert_query")
    print("---------------------------------------------\n")
    cursor.execute(insert_query, (transaction_id, account_number, datetime.now(), transaction_type, amount))
    
    db.commit()
    db.close()
    print(f"{transaction_type} 완료: {amount}원이 계좌에 반영되었습니다.")


# 신규 사용자 및 계좌 생성 함수
def create_user_account(user_data, account_data):
    db = connect_db()
    cursor = db.cursor()
    user_query = "INSERT INTO 사용자 (사용자_ID, 이름, 성별, 연락처, 주민번호, 지점_ID) VALUES (%s, %s, %s, %s, %s, %s);"
    print("\n---------------SQL Code Test---------------\n", user_query)
    print("---------------------------------------------\n")
    cursor.execute(user_query, user_data)
    account_query = "INSERT INTO 계좌 (계좌번호, 사용자_ID, 계좌유형, 잔액, 지점_ID) VALUES (%s, %s, %s, %s, %s);"
    print("\n---------------SQL Code Test---------------\n", account_query)
    print("---------------------------------------------\n")
    cursor.execute(account_query, account_data)
    db.commit()
    db.close()
    print("새로운 사용자 및 계좌가 성공적으로 등록되었습니다!")

# 지점별 사용자 조회함수 
def get_branch_accounts(branch_id):
    db = connect_db()
    cursor = db.cursor()
    query = """
    SELECT 지점.위치, 지점.지점장_이름, 지점.직원수, COUNT(사용자.사용자_ID) AS 사용자_수
    FROM 지점
    JOIN 사용자 ON 사용자.지점_ID = 지점.지점_ID
    WHERE 지점.지점_ID = %s
    """
    print("\n---------------SQL Code Test---------------\n", query)
    print("---------------------------------------------\n")
    cursor.execute(query, (branch_id,))
    result = cursor.fetchall()
    db.close()
    return result

# 사용자 화면
def display_menu():
    print("\n<<<<<<<<<< 눈송이 은행에 오신걸 환영합니다!! >>>>>>>>>>\n")
    print("1. 사용자 정보 조회\n")
    print("2. 거래내역 조회\n")
    print("3. 입출금\n")
    print("4. 신규 가입 및 계좌 개설\n")
    print("5. 은행 지점 조회\n")
    print("6. 종료\n")
    choice = input("원하시는 번호를 입력해주세요 : ")
    return choice

while True:
    create_schema()
    choice = display_menu()
    if choice == "1":
        user_id = input("사용자 ID를 입력하세요 : ")
        result = get_user_info(user_id)
        if result:
            for row in result:
                print(f"이름 : '{row[0]}'")
                print(f"성별 : '{row[1]}'")
                print(f"전화번호 : '{row[2]}'")
                print(f"계좌번호 : '{row[3]}'")
        else:
            print("입력하신 사용자아이디가 올바르지 않습니다.")

    elif choice == "2":
        account_number = input("계좌번호를 입력하세요 : ")
        result = get_account_history(account_number)
        if result:
            for row in result:
                print(f"이름 : '{row[0]}'")
                print(f"거래일시 : ({row[1].year}년, {row[1].month}월, {row[1].day}일, {row[1].hour}시:{row[1].minute}분)")
                print(f"거래유형 : '{row[2]}'")        
                print(f"거래금액 : '{row[3]}'")
                print(f"지점위치 : '{row[4]}'")
        else:
            print("입력하신 계좌번호가 올바르지 않습니다.")

    elif choice == "3":
        account_number = input("계좌번호를 입력하세요 : ")
        transaction_type = input("입금 / 출금 : ")
        if transaction_type in ["입금", "출금"]:
            amount = int(input(f"{transaction_type}할 금액을 입력하세요 : "))
            if transaction_type == "출금":
                balance = get_account_balance(account_number)
                if balance is not None and balance >= amount:
                    update_account(account_number, amount, transaction_type)
                    print(f"{amount}원이 출금되었습니다. 잔액: {balance - amount}원")
                else:
                    print("잔액이 부족합니다.")
            else:
                update_account(account_number, amount, transaction_type)
                print(f"{amount}원이 입금되었습니다.")
        else:
            print("잘못입력하셨습니다. (입금/출금) 정확히 입력해주세요.")

    elif choice == "4":
        user_data = (
            input("사용자 ID: "),
            input("이름: "),
            input("성별(M/F): "),
            input("연락처(010-0000-0000): "),
            input("주민번호(900101-1234567): "),
            input("지점 번호 : ")
        )
        account_data = (
            input("계좌번호(4자리): "),
            user_data[0],
            input("계좌유형(저축/당좌/정기예금): "),
            input("초기 잔액: "),
            user_data[5]
        )
        create_user_account(user_data, account_data)

    elif choice == "5":
        branch_id = input("지점 ID를 입력하세요 : ")
        result = get_branch_accounts(branch_id)
        if result:  # 결과가 존재하는지 확인
            for row in result:
                print(f"지점 위치 : '{row[0]}'")
                print(f"지점장 이름 : '{row[1]}'")
                print(f"직원 수 : '{row[2]}'")
                print(f"사용자 수 : '{row[3]}'")
        else:
            print("입력하신 지점은 존재하지 않습니다.")
            
    elif choice == "6":
        print(">>>>>>>>>> 프로그램을 종료합니다! <<<<<<<<<<")
        break

    else:
        print("잘못된 입력입니다. 다시 입력해주세요.")
        