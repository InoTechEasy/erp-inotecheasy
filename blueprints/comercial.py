from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, make_response
from models import (dClientes, dFuncionarios, fPropostas, fPropostaItens, db,
                   dTipo_Lancamento, dTipo_Pagamento, dContas, fLancamentos)
from datetime import datetime, timedelta
import pytz
from decimal import Decimal
import re

comercial_bp = Blueprint('comercial', __name__, url_prefix='/comercial')
tz = pytz.timezone('America/Sao_Paulo')

def gerar_lancamentos_proposta(proposta):
    """Gera lançamentos financeiros automaticamente quando uma proposta é aprovada."""
    # Verificar se já existem lançamentos para esta proposta
    lancamentos_existentes = fLancamentos.query.filter_by(proposta_id=proposta.id).count()
    if lancamentos_existentes > 0:
        return  # Já foram gerados
    
    # Obter tipos de lançamento e pagamento
    tipo_receita = dTipo_Lancamento.query.filter_by(descricao='Receita').first()
    tipo_pagamento_fatura = dTipo_Pagamento.query.filter_by(descricao='Fatura/Prazo').first()
    
    # Obter conta de receita (Desenvolvimento de Software Sob Medida)
    conta_receita = dContas.query.filter_by(nome='Desenvolvimento de Software Sob Medida').first()
    if not conta_receita:
        conta_receita = dContas.query.filter_by(nome='Receita Total').first()
    
    if not tipo_receita or not tipo_pagamento_fatura or not conta_receita:
        return  # Não é possível gerar lançamentos sem as configurações básicas
    
    # Parse das condições de pagamento para determinar parcelas
    # Exemplo: "2x de R$ 1000,00" ou "30/60 dias"
    condicoes = proposta.condicoes_pagamento or ''
    valor_total = proposta.valor_final
    
    # Tentar extrair número de parcelas das condições
    parcelas_match = re.search(r'(\d+)x', condicoes, re.IGNORECASE)
    if parcelas_match:
        num_parcelas = int(parcelas_match.group(1))
    else:
        # Se não especificar, considerar 1 parcela
        num_parcelas = 1
    
    valor_parcela = valor_total / num_parcelas
    
    # Gerar lançamentos para cada parcela
    for i in range(num_parcelas):
        # Calcular data de vencimento (30 dias por parcela)
        dias_vencimento = 30 * (i + 1)
        data_vencimento = datetime.now(tz).date() + timedelta(days=dias_vencimento)
        
        lancamento = fLancamentos(
            id_tipo_lancamento=tipo_receita.id,
            id_tipo_pagamento=tipo_pagamento_fatura.id,
            id_conta=conta_receita.id,
            id_centro_custo=None,  # Opcional
            id_documento=None,  # Opcional
            descricao=f'Parcela {i+1}/{num_parcelas} - {proposta.numero_proposta}',
            valor_original=valor_parcela,
            valor_pago=Decimal('0'),
            data_documento=datetime.now(tz).date(),
            data_vencimento=data_vencimento,
            data_pagamento=None,
            entidade_id=proposta.cliente_id,
            proposta_id=proposta.id,
            projeto_id=None,
            observacoes=f'Lançamento automático da proposta {proposta.numero_proposta}'
        )
        db.session.add(lancamento)
    
    db.session.commit()


@comercial_bp.route('/propostas')
def propostas():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    propostas = fPropostas.query.order_by(fPropostas.CREATED_AT.desc()).all()
    clientes = dClientes.query.all()
    funcionarios = dFuncionarios.query.all()
    
    return render_template('comercial/propostas.html',
                         propostas=propostas,
                         clientes=clientes,
                         funcionarios=funcionarios)

@comercial_bp.route('/propostas/nova')
def nova_proposta():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    clientes = dClientes.query.all()
    funcionarios = dFuncionarios.query.all()
    
    return render_template('comercial/proposta_form.html',
                         proposta=None,
                         clientes=clientes,
                         funcionarios=funcionarios)

@comercial_bp.route('/propostas/editar/<int:id>')
def editar_proposta(id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    proposta = fPropostas.query.get(id)
    if not proposta:
        return redirect(url_for('comercial.propostas'))
    
    clientes = dClientes.query.all()
    funcionarios = dFuncionarios.query.all()
    
    return render_template('comercial/proposta_form.html',
                         proposta=proposta,
                         clientes=clientes,
                         funcionarios=funcionarios)

@comercial_bp.route('/propostas/salvar', methods=['POST'])
def salvar_proposta():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    data = request.get_json()
    
    proposta_id = data.get('id')
    cliente_id = data.get('cliente_id')
    funcionario_id = data.get('funcionario_id')
    data_emissao = data.get('data_emissao')
    data_validade = data.get('data_validade')
    status = data.get('status', 'Rascunho')
    condicoes_pagamento = data.get('condicoes_pagamento')
    observacoes_gerais = data.get('observacoes_gerais')
    desconto_global = Decimal(str(data.get('desconto_global', 0)))
    itens = data.get('itens', [])
    
    # Calcular valor total
    valor_total = Decimal('0')
    for item in itens:
        quantidade = Decimal(str(item.get('quantidade', 0)))
        valor_unitario = Decimal(str(item.get('valor_unitario', 0)))
        valor_total += quantidade * valor_unitario
    
    valor_final = valor_total - desconto_global
    
    if proposta_id:
        # Atualizar proposta existente
        proposta = fPropostas.query.get(int(proposta_id))
        if proposta:
            proposta.cliente_id = int(cliente_id)
            proposta.funcionario_id = int(funcionario_id)
            proposta.data_emissao = datetime.strptime(data_emissao, '%Y-%m-%d').date()
            proposta.data_validade = datetime.strptime(data_validade, '%Y-%m-%d').date()
            proposta.status = status
            proposta.condicoes_pagamento = condicoes_pagamento
            proposta.observacoes_gerais = observacoes_gerais
            proposta.valor_total = valor_total
            proposta.desconto_global = desconto_global
            proposta.valor_final = valor_final
            proposta.UPDATED_AT = datetime.now(tz)
            
            # Remover itens antigos
            fPropostaItens.query.filter_by(proposta_id=proposta.id).delete()
    else:
        # Criar nova proposta
        # Gerar número da proposta
        ano = datetime.now(tz).year
        ultima_proposta = fPropostas.query.filter(
            fPropostas.numero_proposta.like(f'PRP-{ano}-%')
        ).order_by(fPropostas.numero_proposta.desc()).first()
        
        if ultima_proposta:
            ultimo_numero = int(ultima_proposta.numero_proposta.split('-')[-1])
            novo_numero = ultimo_numero + 1
        else:
            novo_numero = 1
        
        numero_proposta = f'PRP-{ano}-{novo_numero:04d}'
        
        proposta = fPropostas(
            numero_proposta=numero_proposta,
            cliente_id=int(cliente_id),
            funcionario_id=int(funcionario_id),
            data_emissao=datetime.strptime(data_emissao, '%Y-%m-%d').date(),
            data_validade=datetime.strptime(data_validade, '%Y-%m-%d').date(),
            status=status,
            condicoes_pagamento=condicoes_pagamento,
            observacoes_gerais=observacoes_gerais,
            valor_total=valor_total,
            desconto_global=desconto_global,
            valor_final=valor_final
        )
        db.session.add(proposta)
        db.session.flush()  # Para obter o ID da proposta
    
    # Adicionar itens
    for idx, item in enumerate(itens):
        quantidade = Decimal(str(item.get('quantidade', 0)))
        valor_unitario = Decimal(str(item.get('valor_unitario', 0)))
        valor_total_item = quantidade * valor_unitario
        
        novo_item = fPropostaItens(
            proposta_id=proposta.id,
            tipo_item=item.get('tipo_item'),
            descricao_curta=item.get('descricao_curta'),
            detalhamento=item.get('detalhamento'),
            quantidade=quantidade,
            valor_unitario=valor_unitario,
            valor_total_item=valor_total_item,
            ordem_exibicao=idx
        )
        db.session.add(novo_item)
    
    db.session.commit()
    
    # Listener: Se o status mudou para "Aprovada", gerar lançamentos financeiros
    if status == 'Aprovada':
        gerar_lancamentos_proposta(proposta)
    
    return jsonify({'success': True, 'id': proposta.id, 'numero_proposta': proposta.numero_proposta})

@comercial_bp.route('/propostas/excluir/<int:id>', methods=['POST'])
def excluir_proposta(id):
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    proposta = fPropostas.query.get(id)
    if proposta:
        db.session.delete(proposta)
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'error': 'Proposta não encontrada'}), 404

@comercial_bp.route('/propostas/pdf/<int:id>')
def gerar_pdf(id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    proposta = fPropostas.query.get(id)
    if not proposta:
        return redirect(url_for('comercial.propostas'))
    
    from flask import render_template_string, url_for
    import os
    
    # Caminho base para imagens
    base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
    logo_path = os.path.join(base_path, 'logo.png')
    
    # Converter logo para base64 se existir
    logo_base64 = None
    if os.path.exists(logo_path):
        import base64
        with open(logo_path, 'rb') as f:
            logo_base64 = base64.b64encode(f.read()).decode('utf-8')
    
    # Renderizar template HTML
    html_content = render_template('comercial/proposta_pdf.html', proposta=proposta, logo_base64=logo_base64)
    
    # Gerar PDF usando xhtml2pdf
    try:
        from xhtml2pdf import pisa
        from io import BytesIO
        
        # Criar PDF
        pdf_bytes = BytesIO()
        pisa.CreatePDF(
            html_content,
            dest=pdf_bytes,
            encoding='utf-8',
            link_callback=lambda uri, rel: os.path.join(base_path, uri.replace('/static/', ''))
        )
        
        pdf_bytes.seek(0)
        response = make_response(pdf_bytes.read())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=proposta_{proposta.numero_proposta}.pdf'
        
        return response
    except ImportError:
        return jsonify({'error': 'xhtml2pdf não está instalado. Execute: pip install xhtml2pdf'}), 500
    except Exception as e:
        return jsonify({'error': f'Erro ao gerar PDF: {str(e)}'}), 500

@comercial_bp.route('/clientes')
def clientes():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    clientes = dClientes.query.order_by(dClientes.nome_razao_social).all()
    
    return render_template('comercial/clientes.html', clientes=clientes)

@comercial_bp.route('/clientes/salvar', methods=['POST'])
def salvar_cliente():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    id_cliente = request.form.get('id_cliente')
    tipo_pessoa = request.form.get('tipo_pessoa')
    cpf_cnpj = request.form.get('cpf_cnpj')
    nome_razao_social = request.form.get('nome_razao_social')
    email = request.form.get('email')
    telefone = request.form.get('telefone')
    endereco_completo = request.form.get('endereco_completo')
    
    try:
        if id_cliente and id_cliente.strip():
            # Atualizar
            cliente = dClientes.query.get(int(id_cliente))
            if cliente:
                cliente.tipo_pessoa = tipo_pessoa
                cliente.cpf_cnpj = cpf_cnpj
                cliente.nome_razao_social = nome_razao_social
                cliente.email = email
                cliente.telefone = telefone
                cliente.endereco_completo = endereco_completo
                cliente.UPDATED_AT = datetime.now(tz)
                db.session.commit()
                return jsonify({'success': True, 'id': cliente.id, 'action': 'update'})
        else:
            # Criar novo
            cliente = dClientes(
                tipo_pessoa=tipo_pessoa,
                cpf_cnpj=cpf_cnpj,
                nome_razao_social=nome_razao_social,
                email=email,
                telefone=telefone,
                endereco_completo=endereco_completo
            )
            db.session.add(cliente)
            db.session.commit()
            return jsonify({'success': True, 'id': cliente.id, 'action': 'create'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    
    return jsonify({'error': 'Erro ao salvar'}), 400

@comercial_bp.route('/clientes/excluir/<int:id>', methods=['POST'])
def excluir_cliente(id):
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    cliente = dClientes.query.get(id)
    if cliente:
        db.session.delete(cliente)
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'error': 'Cliente não encontrado'}), 404
