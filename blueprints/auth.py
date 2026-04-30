from flask import Blueprint, render_template, request, redirect, url_for, session
from models import fUsuarios, db

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = fUsuarios.query.filter_by(NOME_USUARIO=username, SENHA_USUARIO=password).first()
        
        if user:
            session['user_id'] = user.id
            session['username'] = user.NOME_USUARIO
            return redirect(url_for('main.home'))
        else:
            return render_template('login.html', error='Usuário ou senha inválidos')
    
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
