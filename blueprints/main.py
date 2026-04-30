from flask import Blueprint, render_template, redirect, url_for, session

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return redirect(url_for('main.home'))

@main_bp.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('home.html')

@main_bp.route('/dashboards')
def dashboards():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('dashboards.html')

@main_bp.route('/financeiro')
def financeiro():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('financeiro.html')

@main_bp.route('/configuracoes')
def configuracoes():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('configuracoes.html')

@main_bp.route('/estoque')
def estoque():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('estoque.html')

@main_bp.route('/pdv')
def pdv():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('pdv.html')

@main_bp.route('/comercial')
def comercial():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('comercial.html')
