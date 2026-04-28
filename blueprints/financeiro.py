from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from models import (fLancamentos, dTipo_Lancamento, dTipo_Pagamento, dDocumentos, 
                   dCentros_Custos, dContas, dClientes, db)
from datetime import datetime
import pytz
from decimal import Decimal

financeiro_bp = Blueprint('financeiro', __name__, url_prefix='/financeiro')
tz = pytz.timezone('America/Sao_Paulo')

@financeiro_bp.route('/lancamentos')
def lancamentos():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    lancamentos = fLancamentos.query.order_by(fLancamentos.data_vencimento.desc()).all()
    tipos_lancamento = dTipo_Lancamento.query.all()
    tipos_pagamento = dTipo_Pagamento.query.all()
    documentos = dDocumentos.query.all()
    centros_custo = dCentros_Custos.query.all()
    contas = dContas.query.all()
    clientes = dClientes.query.all()
    
    return render_template('financeiro/lancamentos.html',
                         lancamentos=lancamentos,
                         tipos_lancamento=tipos_lancamento,
                         tipos_pagamento=tipos_pagamento,
                         documentos=documentos,
                         centros_custo=centros_custo,
                         contas=contas,
                         clientes=clientes)

@financeiro_bp.route('/lancamentos/novo')
def novo_lancamento():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    tipos_lancamento = dTipo_Lancamento.query.all()
    tipos_pagamento = dTipo_Pagamento.query.all()
    documentos = dDocumentos.query.all()
    centros_custo = dCentros_Custos.query.all()
    contas = dContas.query.all()
    clientes = dClientes.query.all()
    
    return render_template('financeiro/lancamento_form.html',
                         lancamento=None,
                         tipos_lancamento=tipos_lancamento,
                         tipos_pagamento=tipos_pagamento,
                         documentos=documentos,
                         centros_custo=centros_custo,
                         contas=contas,
                         clientes=clientes)

@financeiro_bp.route('/lancamentos/editar/<int:id>')
def editar_lancamento(id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    lancamento = fLancamentos.query.get(id)
    if not lancamento:
        return redirect(url_for('financeiro.lancamentos'))
    
    tipos_lancamento = dTipo_Lancamento.query.all()
    tipos_pagamento = dTipo_Pagamento.query.all()
    documentos = dDocumentos.query.all()
    centros_custo = dCentros_Custos.query.all()
    contas = dContas.query.all()
    clientes = dClientes.query.all()
    
    return render_template('financeiro/lancamento_form.html',
                         lancamento=lancamento,
                         tipos_lancamento=tipos_lancamento,
                         tipos_pagamento=tipos_pagamento,
                         documentos=documentos,
                         centros_custo=centros_custo,
                         contas=contas,
                         clientes=clientes)

@financeiro_bp.route('/lancamentos/salvar', methods=['POST'])
def salvar_lancamento():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    data = request.get_json()
    
    lancamento_id = data.get('id')
    id_tipo_lancamento = data.get('id_tipo_lancamento')
    id_tipo_pagamento = data.get('id_tipo_pagamento')
    id_conta = data.get('id_conta')
    id_centro_custo = data.get('id_centro_custo')
    id_documento = data.get('id_documento')
    descricao = data.get('descricao')
    valor_original = Decimal(str(data.get('valor_original', 0)))
    valor_pago = Decimal(str(data.get('valor_pago', 0)))
    data_documento = data.get('data_documento')
    data_vencimento = data.get('data_vencimento')
    data_pagamento = data.get('data_pagamento')
    entidade_id = data.get('entidade_id')
    observacoes = data.get('observacoes')
    
    if lancamento_id:
        # Atualizar lançamento existente
        lancamento = fLancamentos.query.get(int(lancamento_id))
        if lancamento:
            lancamento.id_tipo_lancamento = int(id_tipo_lancamento)
            lancamento.id_tipo_pagamento = int(id_tipo_pagamento)
            lancamento.id_conta = int(id_conta)
            lancamento.id_centro_custo = int(id_centro_custo) if id_centro_custo else None
            lancamento.id_documento = int(id_documento) if id_documento else None
            lancamento.descricao = descricao
            lancamento.valor_original = valor_original
            lancamento.valor_pago = valor_pago
            lancamento.data_documento = datetime.strptime(data_documento, '%Y-%m-%d').date() if data_documento else None
            lancamento.data_vencimento = datetime.strptime(data_vencimento, '%Y-%m-%d').date() if data_vencimento else None
            lancamento.data_pagamento = datetime.strptime(data_pagamento, '%Y-%m-%d').date() if data_pagamento else None
            lancamento.entidade_id = int(entidade_id) if entidade_id else None
            lancamento.observacoes = observacoes
            lancamento.UPDATED_AT = datetime.now(tz)
    else:
        # Criar novo lançamento
        lancamento = fLancamentos(
            id_tipo_lancamento=int(id_tipo_lancamento),
            id_tipo_pagamento=int(id_tipo_pagamento),
            id_conta=int(id_conta),
            id_centro_custo=int(id_centro_custo) if id_centro_custo else None,
            id_documento=int(id_documento) if id_documento else None,
            descricao=descricao,
            valor_original=valor_original,
            valor_pago=valor_pago,
            data_documento=datetime.strptime(data_documento, '%Y-%m-%d').date() if data_documento else None,
            data_vencimento=datetime.strptime(data_vencimento, '%Y-%m-%d').date() if data_vencimento else None,
            data_pagamento=datetime.strptime(data_pagamento, '%Y-%m-%d').date() if data_pagamento else None,
            entidade_id=int(entidade_id) if entidade_id else None,
            observacoes=observacoes
        )
        db.session.add(lancamento)
    
    db.session.commit()
    return jsonify({'success': True, 'id': lancamento.id})

@financeiro_bp.route('/lancamentos/excluir/<int:id>', methods=['POST'])
def excluir_lancamento(id):
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    lancamento = fLancamentos.query.get(id)
    if lancamento:
        # Soft Delete: marcar como cancelado zerando o valor
        lancamento.valor_original = Decimal('0')
        lancamento.valor_pago = Decimal('0')
        lancamento.UPDATED_AT = datetime.now(tz)
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'error': 'Lançamento não encontrado'}), 404

@financeiro_bp.route('/lancamentos/baixar/<int:id>', methods=['POST'])
def baixar_lancamento(id):
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    data = request.get_json()
    valor_pago = Decimal(str(data.get('valor_pago', 0)))
    data_pagamento = data.get('data_pagamento')
    
    lancamento = fLancamentos.query.get(id)
    if lancamento:
        lancamento.valor_pago = valor_pago
        lancamento.data_pagamento = datetime.strptime(data_pagamento, '%Y-%m-%d').date() if data_pagamento else datetime.now(tz).date()
        lancamento.UPDATED_AT = datetime.now(tz)
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'error': 'Lançamento não encontrado'}), 404
