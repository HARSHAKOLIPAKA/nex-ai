import os
import requests
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, User, ChatHistory

app = Flask(__name__)
app.config['SECRET_KEY'] = 'harsha_secret_key_2024'
DATABASE_NAME = 'harsha.db'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_NAME}'

# ==================== NEW API KEY ====================
OPENAI_API_KEY = "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"

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# ============================================
# ROUTES
# ============================================

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('chat'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if not user:
            return render_template('auth.html', error="User not found. Please register.")
        
        if user.password == password:
            login_user(user)
            return redirect(url_for('chat'))
        else:
            return render_template('auth.html', error="Incorrect password.")
            
    return render_template('auth.html', error=None)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('chat'))
        
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            return render_template('auth.html', error="Passwords do not match")
        
        if User.query.filter_by(username=username).first():
            return render_template('auth.html', error="Username already exists")
            
        new_user = User(
            username=username, 
            full_name=full_name, 
            email=email, 
            password=password
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('chat'))
        
    return render_template('auth.html', error=None)

@app.route('/chat')
@login_required
def chat():
    history = ChatHistory.query.filter_by(user_id=current_user.id).order_by(ChatHistory.timestamp.desc()).limit(10).all()
    name = current_user.full_name or current_user.username
    return render_template('chat.html', username=name, history=history)

@app.route('/get_response', methods=['POST'])
@login_required
def get_response():
    data = request.get_json()
    user_msg = data['message']
    
    # Get user's chat history
    history = ChatHistory.query.filter_by(user_id=current_user.id).order_by(ChatHistory.timestamp.desc()).limit(5).all()
    
    # Build conversation messages
    messages = [
        {"role": "system", "content": "You are Harsha's AI, a helpful and smart assistant."}
    ]
    
    for chat in reversed(history):
        messages.append({"role": "user", "content": chat.message})
        messages.append({"role": "assistant", "content": chat.response})
    
    messages.append({"role": "user", "content": user_msg})
    
    try:
        # Call OpenAI API
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-3.5-turbo",
                "messages": messages,
                "max_tokens": 500,
                "temperature": 0.7
            },
            timeout=30
        )
        
        result = response.json()
        print("API Response:", result)
        
        if 'error' in result:
            bot_reply = f"Error: {result['error']['message']}"
        elif 'choices' in result and len(result['choices']) > 0:
            bot_reply = result['choices'][0]['message']['content']
        else:
            bot_reply = "I received an unexpected response. Please try again."
            
    except Exception as e:
        bot_reply = f"Error: {str(e)}"
    
    # Save to database
    chat_entry = ChatHistory(user_id=current_user.id, message=user_msg, response=bot_reply)
    db.session.add(chat_entry)
    db.session.commit()

    return jsonify({'response': bot_reply})

@app.route('/clear_chat')
@login_required
def clear_chat():
    ChatHistory.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    return redirect(url_for('chat'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# ============================================
# MAIN
# ============================================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    print("\n" + "="*50)
    print("🚀 Harsha's AI is running!")
    print("👉 Open http://127.0.0.1:5000")
    print("="*50 + "\n")
    app.run(debug=True)