import os
import uuid
from datetime import datetime, timedelta, timezone

from flask import Flask, render_template, request, redirect, url_for
from azure.data.tables import TableServiceClient

app = Flask(__name__)

# 環境変数から接続文字列を読み込む（コードには書かない）
CONNECTION_STRING = os.environ["AZURE_STORAGE_CONNECTION_STRING"]
TABLE_NAME = "posts"

# Table Storageに接続し、テーブルがなければ作る
service = TableServiceClient.from_connection_string(CONNECTION_STRING)
table = service.create_table_if_not_exists(TABLE_NAME)

# 日本時間
JST = timezone(timedelta(hours=9))


@app.route("/")
def index():
    # テーブルから投稿をすべて取り出す
    messages = list(table.list_entities())
    # 投稿日時の新しい順に並べる
    messages.sort(key=lambda m: m["posted_at"], reverse=True)
    return render_template("index.html", messages=messages)


@app.route("/post", methods=["POST"])
def post():
    # フォームから送られた値を受け取る
    name = request.form.get("name", "").strip()
    text = request.form.get("message", "").strip()

    if text:
        if not name:
            name = "名無し"
        # 1件の投稿（エンティティ）をテーブルに保存する
        table.create_entity({
            "PartitionKey": "board",
            "RowKey": str(uuid.uuid4()),
            "name": name,
            "text": text,
            "posted_at": datetime.now(JST).strftime("%Y/%m/%d %H:%M:%S"),
        })

    # トップページに戻る
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)