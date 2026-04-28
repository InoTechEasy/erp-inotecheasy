from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from models import dFuncionarios, dTipo_Conta, dChave_PIX, dBancos, fDados_Bancarios, db
from datetime import datetime
import pytz

administrativo_bp = Blueprint('administrativo', __name__, url_prefix='/administrativo')
tz = pytz.timezone('America/Sao_Paulo')

@administrativo_bp.route('/funcionarios')
def funcionarios():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    funcionarios = dFuncionarios.query.order_by(dFuncionarios.nome_funcionario).all()
    tipos_conta = dTipo_Conta.query.all()
    tipos_pix = dChave_PIX.query.all()
    bancos = dBancos.query.all()
    
    return render_template('administrativo/funcionarios.html', 
                         funcionarios=funcionarios,
                         tipos_conta=tipos_conta,
                         tipos_pix=tipos_pix,
                         bancos=bancos)

@administrativo_bp.route('/funcionario/salvar', methods=['POST'])
def salvar_funcionario():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    id_funcionario = request.form.get('id_funcionario')
    nome = request.form.get('nome')
    salario = request.form.get('salario')
    
    # Remove formatação BRL e converte para float
    if salario:
        salario = salario.replace('R$', '').replace('.', '').replace(',', '.').strip()
        salario = float(salario) if salario else 0
    else:
        salario = 0
    
    if id_funcionario:
        # Atualizar
        funcionario = dFuncionarios.query.get(int(id_funcionario))
        if funcionario:
            funcionario.nome_funcionario = nome
            funcionario.salario_funcionario = salario
            funcionario.UPDATED_AT = datetime.now(tz)
            db.session.commit()
            return jsonify({'success': True, 'id': funcionario.id_funcionario, 'action': 'update'})
    else:
        # Criar novo
        funcionario = dFuncionarios(
            nome_funcionario=nome,
            salario_funcionario=salario
        )
        db.session.add(funcionario)
        db.session.commit()
        return jsonify({'success': True, 'id': funcionario.id_funcionario, 'action': 'create'})
    
    return jsonify({'error': 'Erro ao salvar'}), 400

@administrativo_bp.route('/funcionario/excluir/<int:id>', methods=['POST'])
def excluir_funcionario(id):
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    funcionario = dFuncionarios.query.get(id)
    if funcionario:
        db.session.delete(funcionario)
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'error': 'Funcionário não encontrado'}), 404

@administrativo_bp.route('/dados-bancarios/salvar', methods=['POST'])
def salvar_dados_bancarios():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    id_dados = request.form.get('id_dados')
    id_funcionario = request.form.get('id_funcionario')
    id_banco = request.form.get('id_banco')
    tipo_conta = request.form.get('tipo_conta')
    nome_titular = request.form.get('nome_titular')
    tipo_chave_pix = request.form.get('tipo_chave_pix')
    chave_pix = request.form.get('chave_pix')
    
    if id_dados:
        # Atualizar
        dados = fDados_Bancarios.query.get(int(id_dados))
        if dados:
            dados.id_banco = int(id_banco) if id_banco else None
            dados.tipo_conta = tipo_conta
            dados.nome_titular = nome_titular
            dados.tipo_chave_pix = tipo_chave_pix
            dados.chave_pix = chave_pix
            dados.UPDATED_AT = datetime.now(tz)
            db.session.commit()
            return jsonify({'success': True, 'action': 'update'})
    else:
        # Criar novo
        dados = fDados_Bancarios(
            id_banco=int(id_banco) if id_banco else None,
            tipo_conta=tipo_conta,
            nome_titular=nome_titular,
            tipo_chave_pix=tipo_chave_pix,
            chave_pix=chave_pix,
            id_funcionario=int(id_funcionario) if id_funcionario else None
        )
        db.session.add(dados)
        db.session.commit()
        return jsonify({'success': True, 'action': 'create'})
    
    return jsonify({'error': 'Erro ao salvar'}), 400

@administrativo_bp.route('/dados-bancarios/excluir/<int:id>', methods=['POST'])
def excluir_dados_bancarios(id):
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    dados = fDados_Bancarios.query.get(id)
    if dados:
        db.session.delete(dados)
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'error': 'Dados bancários não encontrados'}), 404

@administrativo_bp.route('/funcionario/<int:id>')
def funcionario_detalhes(id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    funcionario = dFuncionarios.query.get(id)
    if not funcionario:
        return redirect(url_for('administrativo.funcionarios'))
    
    tipos_conta = dTipo_Conta.query.all()
    tipos_pix = dChave_PIX.query.all()
    bancos = dBancos.query.all()
    
    return render_template('administrativo/funcionario_detalhes.html',
                         funcionario=funcionario,
                         tipos_conta=tipos_conta,
                         tipos_pix=tipos_pix,
                         bancos=bancos)
