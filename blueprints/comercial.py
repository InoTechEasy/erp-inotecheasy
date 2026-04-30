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
    
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
    from reportlab.platypus.tableofcontents import TableOfContents
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_JUSTIFY, TA_LEFT
    from reportlab.pdfgen import canvas
    from io import BytesIO
    import os
    import base64
    
    # Cores do template HTML
    COLOR_PRIMARY = colors.HexColor('#143060')  # Azul escuro
    COLOR_SECONDARY = colors.HexColor('#2698BE')  # Azul claro
    COLOR_DETAIL = colors.HexColor('#15507D')  # Azul médio
    
    # Caminho da logo
    base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
    logo_path = os.path.join(base_path, 'logo.png')
    
    # Criar PDF
    pdf_bytes = BytesIO()
    doc = SimpleDocTemplate(pdf_bytes, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=1*cm, bottomMargin=2.5*cm)
    
    # Estilos
    styles = getSampleStyleSheet()
    header_style = ParagraphStyle('Header', parent=styles['Normal'], fontSize=9, textColor=COLOR_PRIMARY, spaceBefore=3, spaceAfter=3, alignment=TA_RIGHT)
    title_style = ParagraphStyle('Title', parent=styles['Heading2'], fontSize=14, textColor=COLOR_PRIMARY, spaceAfter=15, spaceBefore=15)
    normal_style = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=9, textColor=COLOR_DETAIL, spaceAfter=5)
    justified_style = ParagraphStyle('Justified', parent=styles['Normal'], fontSize=9, textColor=COLOR_DETAIL, spaceAfter=5, alignment=TA_JUSTIFY)
    cell_style = ParagraphStyle('Cell', parent=styles['Normal'], fontSize=9, textColor=COLOR_DETAIL)
    header_cell_style = ParagraphStyle('HeaderCell', parent=styles['Normal'], fontSize=12, textColor=colors.white, fontName='Helvetica-Bold')
    
    # Variável para controle de páginas
    page_num = [0]
    
    # Função para desenhar marca d'água e rodapé
    def footer(canvas, doc):
        canvas.saveState()
        page_num[0] += 1
        
        # Marca d'água com logo (se existir)
        if os.path.exists(logo_path):
            try:
                canvas.saveState()
                canvas.setFillColor(COLOR_SECONDARY)
                canvas.setFillAlpha(0.1)
                canvas.drawImage(logo_path, 5*cm, 10*cm, width=10*cm, height=10*cm, mask='auto')
                canvas.restoreState()
            except:
                pass
        
        # Linha separadora no topo do rodapé
        canvas.setStrokeColor(COLOR_SECONDARY)
        canvas.setLineWidth(2)
        canvas.line(2*cm, 2.5*cm, 19*cm, 2.5*cm)
        
        # Texto de validade
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(COLOR_DETAIL)
        validade_text = f'Esta proposta é válida até {proposta.data_validade.strftime("%d/%m/%Y") if proposta.data_validade else ""}'
        canvas.drawCentredString(10.5*cm, 1.8*cm, validade_text)
        
        # Número de página no canto inferior direito
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(COLOR_PRIMARY)
        canvas.drawRightString(19*cm, 1*cm, f'Página {page_num[0]}')
        
        canvas.restoreState()
    
    # Conteúdo do PDF
    story = []
    
    # Cabeçalho com logo (esquerda) e informações da empresa + cliente (direita)
    # Dados da empresa
    company_data = [
        f'<b>InoTechEasy - Serviços Inteligentes</b>',
        f'<b>CPF:</b> 024.805.230-63',
        f'<b>ENDEREÇO:</b> Rua Ribeira 33, Jardim do Trevo, Campinas/BR',
        f'<b>E-MAIL:</b> inotecheasy@gmail.com',
        f'<b>PROPOSTA:</b> {proposta.numero_proposta}',
        f'<b>GERADA EM:</b> {proposta.CREATED_AT.strftime("%d/%m/%Y %H:%M") if proposta.CREATED_AT else ""}',
        f'<b>RESPONSÁVEL:</b> LEONARDO FEIJO DORNELES AGUIAR',
        f'<b>VALIDADE:</b> {proposta.data_validade.strftime("%d/%m/%Y") if proposta.data_validade else ""}'
    ]
    
    # Dados do cliente (seguindo na sequência)
    if proposta.cliente:
        company_data.append('<b>DADOS DO CLIENTE:</b>')
        company_data.append(f'<b>{proposta.cliente.nome_razao_social}</b>')
        company_data.append(f'<b>CNPJ/CPF:</b> {proposta.cliente.cpf_cnpj}')
        company_data.append(f'<b>ENDEREÇO:</b> {proposta.cliente.endereco_completo or "-"}')
        company_data.append(f'<b>E-MAIL:</b> {proposta.cliente.email or "-"}')
        company_data.append(f'<b>TELEFONE:</b> {proposta.cliente.telefone or "-"}')
    
    company_paragraphs = [Paragraph(text, header_style) for text in company_data]
    
    # Logo na esquerda e dados à direita na mesma linha
    if os.path.exists(logo_path):
        try:
            logo_img = Image(logo_path, width=2.64*cm, height=2.64*cm)
            header_table = Table([[logo_img, company_paragraphs]], colWidths=[3.2*cm, 12.8*cm])
            header_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            story.append(header_table)
        except:
            for p in company_paragraphs:
                story.append(p)
    else:
        for p in company_paragraphs:
            story.append(p)
    
    story.append(Spacer(1, 0.5*cm))
    
    # Itens da proposta
    story.append(Paragraph("Itens da Proposta", title_style))
    
    # Tabela de itens com Paragraph para quebra de texto
    itens_data = [[Paragraph('Tipo', header_cell_style), Paragraph('Descrição', header_cell_style), Paragraph('Detalhamento', header_cell_style), 
                   Paragraph('Qtd', header_cell_style), Paragraph('Vlr. Unit', header_cell_style), Paragraph('Vlr. Total', header_cell_style)]]
    
    for item in sorted(proposta.itens, key=lambda x: x.ordem_exibicao):
        itens_data.append([
            Paragraph(item.tipo_item, cell_style),
            Paragraph(item.descricao_curta, cell_style),
            Paragraph(item.detalhamento or '', cell_style),
            Paragraph(str(float(item.quantidade)), cell_style),
            Paragraph(f'R$ {float(item.valor_unitario):.2f}'.replace('.', ','), cell_style),
            Paragraph(f'R$ {float(item.valor_total_item):.2f}'.replace('.', ','), cell_style)
        ])
    
    # Linhas de subtotal - usando Paragraph para renderizar HTML corretamente
    itens_data.append(['', '', '', '', 
                      Paragraph('<b>Subtotal:</b>', ParagraphStyle('FooterLabel', parent=cell_style, textColor=colors.white)), 
                      Paragraph(f'<b>R$ {float(proposta.valor_total):.2f}</b>'.replace('.', ','), ParagraphStyle('FooterValue', parent=cell_style, textColor=colors.white))])
    
    if proposta.desconto_global and float(proposta.desconto_global) > 0:
        itens_data.append(['', '', '', '', 
                          Paragraph('<b>Desconto:</b>', ParagraphStyle('FooterLabel', parent=cell_style, textColor=colors.white)), 
                          Paragraph(f'<b>R$ {float(proposta.desconto_global):.2f}</b>'.replace('.', ','), ParagraphStyle('FooterValue', parent=cell_style, textColor=colors.white))])
    
    itens_data.append(['', '', '', '', 
                      Paragraph('<b>Valor Final:</b>', ParagraphStyle('FooterLabel', parent=cell_style, textColor=colors.white)), 
                      Paragraph(f'<b>R$ {float(proposta.valor_final):.2f}</b>'.replace('.', ','), ParagraphStyle('FooterValue', parent=cell_style, textColor=colors.white))])
    
    # Ajustar larguras das colunas para melhor quebra de texto
    itens_table = Table(itens_data, colWidths=[2*cm, 3*cm, 4.5*cm, 1.5*cm, 2.5*cm, 2.5*cm], repeatRows=1)
    
    # Definir estilos para a tabela com bordas completas
    table_style = [
        ('BACKGROUND', (0, 0), (-1, 0), COLOR_SECONDARY),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
        ('GRID', (0, 0), (-1, -1), 1, COLOR_SECONDARY),  # Bordas em toda a tabela
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TEXTCOLOR', (0, 1), (-1, -1), COLOR_DETAIL),
        ('FONTSTYLE', (2, 1), (2, -len(itens_data)+4), 'ITALIC'),
    ]
    
    # Estilizar linhas de total
    last_rows = len(itens_data) - (3 if proposta.desconto_global and float(proposta.desconto_global) > 0 else 2)
    table_style.extend([
        ('BACKGROUND', (0, last_rows), (-1, -1), COLOR_SECONDARY),
        ('TEXTCOLOR', (0, last_rows), (-1, -1), colors.white),
        ('FONTNAME', (0, last_rows), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 12),
    ])
    
    itens_table.setStyle(TableStyle(table_style))
    story.append(itens_table)
    story.append(Spacer(1, 0.5*cm))
    
    # Condições de pagamento
    if proposta.condicoes_pagamento:
        story.append(Paragraph("Condições de Pagamento", title_style))
        story.append(Paragraph(proposta.condicoes_pagamento, normal_style))
        story.append(Spacer(1, 0.5*cm))
    
    # Observações com texto justificado
    if proposta.observacoes_gerais:
        story.append(Paragraph("Observações Gerais", title_style))
        story.append(Paragraph(proposta.observacoes_gerais, justified_style))
        story.append(Spacer(1, 0.5*cm))
    
    # Área de assinaturas - separadas por entidade
    story.append(Spacer(1, 2*cm))
    
    # Assinatura do cliente
    if proposta.cliente:
        story.append(Paragraph(f"<b>{proposta.cliente.nome_razao_social}</b>", header_style))
        story.append(Paragraph("Assinatura", header_style))
        story.append(Paragraph("Data: ___/___/_______", header_style))
        story.append(Spacer(1, 1*cm))
    
    # Assinatura do responsável
    story.append(Paragraph("<b>LEONARDO FEIJO DORNELES AGUIAR</b>", header_style))
    story.append(Paragraph("Assinatura", header_style))
    story.append(Paragraph("Data: ___/___/_______", header_style))
    
    # Gerar PDF com rodapé e marca d'água
    try:
        doc.build(story, onFirstPage=footer, onLaterPages=footer)
        
        pdf_bytes.seek(0)
        response = make_response(pdf_bytes.read())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=proposta_{proposta.numero_proposta}.pdf'
        return response
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
