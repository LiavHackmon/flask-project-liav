from flask import Flask, request, redirect, render_template
import sqlite3
import requests
from discordwebhook import Discord
from datetime import datetime, timedelta

app=Flask(__name__)  
discord_url = 'https://discord.com/api/webhooks/1338810174336532552/uFNaPbnJzoEln3OKtIMtf_b8t1Okn6hyeFcvtdAPR8FeGRiEkNu9gRWap2EUPcLM5je7' #my url to discord

@app.route('/')
def home():
    return render_template('index.html')

def create_table():
    conn = sqlite3.connect('messages.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            time DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
create_table()

def send_to_discord(message):
    data_dict = {
        "content": message } 
    response = requests.post(discord_url, json=data_dict) #מכניס את ההודעה לתוך הדיסקורד
    if response.status_code == 204:  
        print("its good")
    else: 
        print(f"error: {response.status_code}")
    return redirect('/text_received')    

@app.route('/add_text', methods=['POST'])
def add_text():
    try:
        text = request.form['text']
        if not text:
            return "there is not text"
        conn = sqlite3.connect('messages.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO messages (content) VALUES (?)', (text,))
        conn.commit()
    except Exception as e:
        return f"error: {e}", 500 
    finally:
        conn.close()
    return redirect('/text_received')

@app.route('/text_received')
def text_received():
    conn = sqlite3.connect('messages.db')
    cursor = conn.cursor()
    cursor.execute('SELECT content FROM messages WHERE id = (SELECT MAX(id) FROM messages)')
    the_content=cursor.fetchone()
    send_to_discord(the_content[0])
    conn.close()
    return 'content sent to discord '

@app.route('/messages') 
def messages():
    conn = sqlite3.connect('messages.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM messages')
    rows=cursor.fetchall()
    conn.close()
    return render_template('messages.html', messages=rows)

@app.route('/last_messages') 
def last_messages():
    conn = sqlite3.connect('messages.db')
    cursor = conn.cursor()
    current_time = datetime.now()
    last_content = current_time - timedelta(minutes=150)
    last_content = last_content.strftime('%Y-%m-%d %H:%M:%S') #העתקה מהצאט
    cursor.execute('SELECT time,content FROM messages WHERE time >= ?', (last_content,))
    rows=cursor.fetchall()
    conn.close()
    return render_template('lastM.html', messages=rows)



if __name__=='__main__':   
    app.run(debug=True)

