from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz

db = SQLAlchemy()
tz = pytz.timezone('America/Sao_Paulo')

class fUsuarios(db.Model):
    __tablename__ = 'fUsuarios'
    id = db.Column(db.Integer, primary_key=True)
    NOME_USUARIO = db.Column(db.String(100), nullable=False)
    SENHA_USUARIO = db.Column(db.String(255), nullable=False)
    CREATED_AT = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(tz))
    UPDATED_AT = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(tz), onupdate=lambda: datetime.now(tz))

class dTipo_Conta(db.Model):
    __tablename__ = 'dTipo_Conta'
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(50), nullable=False)
    CREATED_AT = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(tz))
    UPDATED_AT = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(tz), onupdate=lambda: datetime.now(tz))

class dChave_PIX(db.Model):
    __tablename__ = 'dChave_PIX'
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(50), nullable=False)
    CREATED_AT = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(tz))
    UPDATED_AT = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(tz), onupdate=lambda: datetime.now(tz))

class dBancos(db.Model):
    __tablename__ = 'dBancos'
    ID_BANCO = db.Column(db.Integer, primary_key=True)
    NOME_BANCO = db.Column(db.String(100), nullable=False)
    COD_BANCO = db.Column(db.String(10), nullable=False)
    CREATED_AT = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(tz))
    UPDATED_AT = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(tz), onupdate=lambda: datetime.now(tz))
    
    dados_bancarios = db.relationship('fDados_Bancarios', backref='banco', lazy=True)

class dFuncionarios(db.Model):
    __tablename__ = 'dFuncionarios'
    id_funcionario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome_funcionario = db.Column(db.String(100), nullable=False)
    salario_funcionario = db.Column(db.Float, nullable=False)
    CREATED_AT = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(tz))
    UPDATED_AT = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(tz), onupdate=lambda: datetime.now(tz))
    
    dados_bancarios = db.relationship('fDados_Bancarios', backref='funcionario', lazy=True, cascade='all, delete-orphan')
    atestados = db.relationship('fAtestados', backref='funcionario', lazy=True, cascade='all, delete-orphan')
    ferias = db.relationship('fFerias', backref='funcionario', lazy=True, cascade='all, delete-orphan')

class fDados_Bancarios(db.Model):
    __tablename__ = 'fDados_Bancarios'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_banco = db.Column(db.Integer, db.ForeignKey('dBancos.ID_BANCO'), nullable=False)
    tipo_conta = db.Column(db.Integer, db.ForeignKey('dTipo_Conta.id'), nullable=False)
    nome_titular = db.Column(db.String(100), nullable=False)
    tipo_chave_pix = db.Column(db.Integer, db.ForeignKey('dChave_PIX.id'), nullable=False)
    chave_pix = db.Column(db.String(255), nullable=False)
    id_funcionario = db.Column(db.Integer, db.ForeignKey('dFuncionarios.id_funcionario'), nullable=False)
    CREATED_AT = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(tz))
    UPDATED_AT = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(tz), onupdate=lambda: datetime.now(tz))
    
    tipo_conta_obj = db.relationship('dTipo_Conta', backref='dados_bancarios')
    tipo_chave_pix_obj = db.relationship('dChave_PIX', backref='dados_bancarios')

class fAtestados(db.Model):
    __tablename__ = 'fAtestados'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_funcionario = db.Column(db.Integer, db.ForeignKey('dFuncionarios.id_funcionario'), nullable=False)
    data_atestado = db.Column(db.Date, nullable=False)
    dias_afastamento = db.Column(db.Integer, nullable=False)
    cid = db.Column(db.String(10), nullable=False)
    medico = db.Column(db.String(100), nullable=False)
    observacao = db.Column(db.Text)
    CREATED_AT = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(tz))
    UPDATED_AT = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(tz), onupdate=lambda: datetime.now(tz))

class fFerias(db.Model):
    __tablename__ = 'fFerias'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_funcionario = db.Column(db.Integer, db.ForeignKey('dFuncionarios.id_funcionario'), nullable=False)
    data_inicio = db.Column(db.Date, nullable=False)
    data_fim = db.Column(db.Date, nullable=False)
    dias_ferias = db.Column(db.Integer, nullable=False)
    observacao = db.Column(db.Text)
    CREATED_AT = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(tz))
    UPDATED_AT = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(tz), onupdate=lambda: datetime.now(tz))

class dClientes(db.Model):
    __tablename__ = 'dClientes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tipo_pessoa = db.Column(db.String(1), nullable=False)
    cpf_cnpj = db.Column(db.String(18), nullable=False, unique=True)
    nome_razao_social = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(100))
    telefone = db.Column(db.String(20))
    endereco_completo = db.Column(db.Text)
    CREATED_AT = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(tz))
    UPDATED_AT = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(tz), onupdate=lambda: datetime.now(tz))
    
    propostas = db.relationship('fPropostas', backref='cliente', lazy=True)

class fPropostas(db.Model):
    __tablename__ = 'fPropostas'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    numero_proposta = db.Column(db.String(20), nullable=False, unique=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('dClientes.id'), nullable=False)
    funcionario_id = db.Column(db.Integer, db.ForeignKey('dFuncionarios.id_funcionario'), nullable=False)
    data_emissao = db.Column(db.Date, nullable=False, default=lambda: datetime.now(tz).date())
    data_validade = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Rascunho')
    condicoes_pagamento = db.Column(db.Text)
    observacoes_gerais = db.Column(db.Text)
    valor_total = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    desconto_global = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    valor_final = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    CREATED_AT = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(tz))
    UPDATED_AT = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(tz), onupdate=lambda: datetime.now(tz))
    
    funcionario = db.relationship('dFuncionarios', backref='propostas')
    itens = db.relationship('fPropostaItens', backref='proposta', lazy=True, cascade='all, delete-orphan')

class fPropostaItens(db.Model):
    __tablename__ = 'fPropostaItens'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    proposta_id = db.Column(db.Integer, db.ForeignKey('fPropostas.id'), nullable=False)
    tipo_item = db.Column(db.String(30), nullable=False)
    descricao_curta = db.Column(db.String(255), nullable=False)
    detalhamento = db.Column(db.Text)
    quantidade = db.Column(db.Numeric(10, 2), nullable=False)
    valor_unitario = db.Column(db.Numeric(12, 2), nullable=False)
    valor_total_item = db.Column(db.Numeric(12, 2), nullable=False)
    ordem_exibicao = db.Column(db.Integer, nullable=False, default=0)
    CREATED_AT = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(tz))
    UPDATED_AT = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(tz), onupdate=lambda: datetime.now(tz))

# ==================== MODULO FINANCEIRO ====================

class dTipo_Lancamento(db.Model):
    __tablename__ = 'dTipo_Lancamento'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descricao = db.Column(db.String(50), nullable=False)
    CREATED_AT = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(tz))
    UPDATED_AT = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(tz), onupdate=lambda: datetime.now(tz))
    
    lancamentos = db.relationship('fLancamentos', backref='tipo_lancamento', lazy=True)

class dTipo_Pagamento(db.Model):
    __tablename__ = 'dTipo_Pagamento'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descricao = db.Column(db.String(50), nullable=False)
    CREATED_AT = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(tz))
    UPDATED_AT = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(tz), onupdate=lambda: datetime.now(tz))
    
    lancamentos = db.relationship('fLancamentos', backref='tipo_pagamento', lazy=True)

class dDocumentos(db.Model):
    __tablename__ = 'dDocumentos'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descricao = db.Column(db.String(100), nullable=False)
    CREATED_AT = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(tz))
    UPDATED_AT = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(tz), onupdate=lambda: datetime.now(tz))
    
    lancamentos = db.relationship('fLancamentos', backref='tipo_documento', lazy=True)

class dCentros_Custos(db.Model):
    __tablename__ = 'dCentros_Custos'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descricao = db.Column(db.String(100), nullable=False)
    CREATED_AT = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(tz))
    UPDATED_AT = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(tz), onupdate=lambda: datetime.now(tz))
    
    lancamentos = db.relationship('fLancamentos', backref='centro_custo', lazy=True)

class dContas(db.Model):
    __tablename__ = 'dContas'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_pai = db.Column(db.Integer, db.ForeignKey('dContas.id'), nullable=True)
    nome = db.Column(db.String(100), nullable=False)
    tipo_dre = db.Column(db.String(50), nullable=False)
    CREATED_AT = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(tz))
    UPDATED_AT = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(tz), onupdate=lambda: datetime.now(tz))
    
    # Self-reference para hierarquia
    filhas = db.relationship('dContas', backref=db.backref('pai', remote_side=[id]), lazy=True)
    lancamentos = db.relationship('fLancamentos', backref='conta', lazy=True)

class fLancamentos(db.Model):
    __tablename__ = 'fLancamentos'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_tipo_lancamento = db.Column(db.Integer, db.ForeignKey('dTipo_Lancamento.id'), nullable=False)
    id_tipo_pagamento = db.Column(db.Integer, db.ForeignKey('dTipo_Pagamento.id'), nullable=False)
    id_conta = db.Column(db.Integer, db.ForeignKey('dContas.id'), nullable=False)
    id_centro_custo = db.Column(db.Integer, db.ForeignKey('dCentros_Custos.id'), nullable=True)
    id_documento = db.Column(db.Integer, db.ForeignKey('dDocumentos.id'), nullable=True)
    descricao = db.Column(db.String(255), nullable=False)
    valor_original = db.Column(db.Numeric(15, 2), nullable=False)
    valor_pago = db.Column(db.Numeric(15, 2), nullable=False, default=0)
    data_documento = db.Column(db.Date, nullable=True)
    data_vencimento = db.Column(db.Date, nullable=True)
    data_pagamento = db.Column(db.Date, nullable=True)
    entidade_id = db.Column(db.Integer, db.ForeignKey('dClientes.id'), nullable=True)
    proposta_id = db.Column(db.Integer, db.ForeignKey('fPropostas.id'), nullable=True)
    projeto_id = db.Column(db.Integer, nullable=True)
    observacoes = db.Column(db.Text)
    CREATED_AT = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(tz))
    UPDATED_AT = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(tz), onupdate=lambda: datetime.now(tz))
    
    cliente = db.relationship('dClientes', backref='lancamentos')
    proposta = db.relationship('fPropostas', backref='lancamentos')
    
    @property
    def status_calculado(self):
        """Calcula o status baseado em data_pagamento, data_vencimento e data atual."""
        from datetime import date
        
        # Se já foi pago
        if self.data_pagamento and self.valor_pago > 0:
            tipo = self.tipo_lancamento.descricao if self.tipo_lancamento else ''
            if tipo == 'Receita':
                return 'RECEBIDO'
            else:
                return 'PAGO'
        
        # Se não foi pago, verificar vencimento
        if self.data_vencimento:
            hoje = date.today()
            if self.data_vencimento < hoje:
                return 'ATRASADO'
            else:
                return 'PENDENTE'
        
        # Sem data de vencimento
        return 'PENDENTE'
