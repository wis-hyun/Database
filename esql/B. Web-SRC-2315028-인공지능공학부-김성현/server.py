from flask import Flask, jsonify, request
from datetime import datetime
import mysql.connector
from flask_cors import CORS
import logging
from decimal import Decimal

app = Flask(__name__)
CORS(app)

# 로깅 설정
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")

# 데이터베이스 연결 함수
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="khyun0303",
        database="ESQL"
    )

# 공통 함수: SELECT 쿼리 실행
def execute_select_query(query, params):
    with connect_db() as db:
        with db.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()

# 공통 함수: INSERT/UPDATE 쿼리 실행
def execute_commit_query(query, params):
    with connect_db() as db:
        with db.cursor() as cursor:
            cursor.execute(query, params)
            db.commit()

# 사용자 정보 조회 API
@app.route('/user/<int:user_id>', methods=['GET'])
def get_user_info(user_id):
    query = """
    SELECT 사용자.이름, 사용자.성별, 사용자.연락처, 계좌.계좌번호
    FROM 사용자
    JOIN 계좌 ON 사용자.사용자_ID = 계좌.사용자_ID
    WHERE 사용자.사용자_ID = %s;
    """
    result = execute_select_query(query, (user_id,))
    data = [{"이름": r[0], "성별": r[1], "연락처": r[2], "계좌번호": r[3]} for r in result]
    return jsonify(data)

# 거래내역 조회 API
@app.route('/account/history/<int:account_number>/transactions', methods=['GET'])
def get_account_history(account_number):
    query = """
    SELECT 사용자.이름, 거래내역.거래일시, 거래내역.거래유형, 거래내역.거래금액, 지점.위치
    FROM 거래내역
    JOIN 계좌 ON 거래내역.계좌번호 = 계좌.계좌번호
    JOIN 사용자 ON 계좌.사용자_ID = 사용자.사용자_ID
    JOIN 지점 ON 사용자.지점_ID = 지점.지점_ID
    WHERE 계좌.계좌번호 = %s;
    """
    result = execute_select_query(query, (account_number,))
    data = [
        {
            "이름": r[0],
            "거래일시": r[1].strftime("%Y-%m-%d %H:%M:%S"),
            "거래유형": r[2],
            "거래금액": r[3],
            "지점위치": r[4]
        } for r in result
    ]
    return jsonify(data)

# 계좌 잔액 조회 API
@app.route('/account/history/<int:account_number>/balance', methods=['GET'])
def get_account_balance(account_number):
    query = "SELECT 잔액 FROM 계좌 WHERE 계좌번호 = %s;"
    result = execute_select_query(query, (account_number,))
    if result:
        return jsonify({"잔액": result[0][0]})
    else:
        return jsonify({"error": "계좌를 찾을 수 없습니다."}), 404

# 잔액 업데이트 API
@app.route('/account/update', methods=['POST'])
def update_account():
    data = request.json
    account_number = data.get('accountNumber')
    amount = Decimal(data.get('amount'))
    transaction_type = data.get('transactionType')
    balance_query = "SELECT 잔액 FROM 계좌 WHERE 계좌번호 = %s;"
    result = execute_select_query(balance_query, (account_number,))
    
    if not result:
        return jsonify({"error": "계좌를 찾을 수 없습니다."}), 404
    current_balance = Decimal(result[0][0])
    if transaction_type == "출금" and current_balance < amount:
        return jsonify({"error": "잔액이 부족합니다."}), 400

    # 잔액 업데이트
    if transaction_type == "입금":
        update_query = "UPDATE 계좌 SET 잔액 = 잔액 + %s WHERE 계좌번호 = %s;"
    elif transaction_type == "출금":
        update_query = "UPDATE 계좌 SET 잔액 = 잔액 - %s WHERE 계좌번호 = %s;"
    else:
        return jsonify({"error": "잘못된 거래 유형입니다."}), 400
    execute_commit_query(update_query, (amount, account_number))

    # 거래내역 기록
    transaction_id_query = "SELECT COALESCE(MAX(거래_ID), 2000) + 1 FROM 거래내역;"
    transaction_id = execute_select_query(transaction_id_query, ())[0][0]
    insert_query = """
    INSERT INTO 거래내역 (거래_ID, 계좌번호, 거래일시, 거래유형, 거래금액)
    VALUES (%s, %s, %s, %s, %s);
    """
    execute_commit_query(insert_query, (transaction_id, account_number, datetime.utcnow(), transaction_type, amount))
    return jsonify({
        "message": f"{transaction_type} 완료: {amount}원이 계좌에 반영되었습니다.",
        "updated_balance": current_balance + (amount if transaction_type == "입금" else -amount)
    })

# 신규 사용자 생성 API
@app.route('/user', methods=['POST'])
def create_user_account():
    data = request.json
    user_data = data["user"]
    account_data = data["account"]
    try:
        user_query = """
        INSERT INTO 사용자 (사용자_ID, 이름, 성별, 연락처, 주민번호, 지점_ID)
        VALUES (%s, %s, %s, %s, %s, %s);
        """
        account_query = """
        INSERT INTO 계좌 (계좌번호, 사용자_ID, 계좌유형, 잔액, 지점_ID)
        VALUES (%s, %s, %s, %s, %s);
        """
        execute_commit_query(user_query, user_data)
        execute_commit_query(account_query, account_data)
        return jsonify({"message": "사용자 및 계좌 생성 성공"})
    except Exception as e:
        logging.error(f"사용자 및 계좌 생성 실패: {str(e)}")
        return jsonify({"error": "사용자 및 계좌 생성 실패"}), 500

# 지점별 사용자 조회 API
@app.route('/branch/<int:branch_id>', methods=['GET'])
def get_branch_accounts(branch_id):
    query = """
    SELECT 지점.위치, 지점.지점장_이름, 지점.직원수, COUNT(사용자.사용자_ID) AS 사용자_수
    FROM 지점
    JOIN 사용자 ON 사용자.지점_ID = 지점.지점_ID
    WHERE 지점.지점_ID = %s
    """
    result = execute_select_query(query, (branch_id,))
    data = [
        {
            "위치": r[0],
            "지점장_이름": r[1],
            "직원수": r[2],
            "사용자_수": r[3]
        } for r in result
    ]
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)