from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import db
from blueprints.main import main_bp
from blueprints.auth import auth_bp
from blueprints.administrativo import administrativo_bp
from blueprints.comercial import comercial_bp
from blueprints.financeiro import financeiro_bp
import pytz

app = Flask(__name__)
app.secret_key = 'chave-secreta-super-segura-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres.jqffbxrohqqymaeulqcd:Bancodaino%40@aws-1-us-west-2.pooler.supabase.com:6543/postgres?sslmode=require'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar o banco de dados
db.init_app(app)

# Registrar Blueprints
app.register_blueprint(main_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(administrativo_bp)
app.register_blueprint(comercial_bp)
app.register_blueprint(financeiro_bp)

# Timezone UTC-3
tz = pytz.timezone('America/Sao_Paulo')

# Filtro customizado para formatar moeda BRL
@app.template_filter('currency_format')
def currency_format(value):
    if value is None:
        return 'R$ 0,00'
    return f'R$ {value:,.2f}'.replace('.', ',')

def init_db():
    with app.app_context():
        from models import (fUsuarios, dTipo_Conta, dChave_PIX, dBancos, dFuncionarios, 
                           dClientes, fPropostas, fPropostaItens, 
                           dTipo_Lancamento, dTipo_Pagamento, dDocumentos, dCentros_Custos, 
                           dContas, fLancamentos)
        db.create_all()
        
        # Verificar se já existem dados
        if fUsuarios.query.count() == 0:
            # Criar usuário admin
            admin = fUsuarios(NOME_USUARIO='admin', SENHA_USUARIO='admin123')
            db.session.add(admin)
            
            # Criar tipos de conta
            tipos_conta = [
                dTipo_Conta(descricao='Corrente'),
                dTipo_Conta(descricao='Poupança')
            ]
            db.session.add_all(tipos_conta)
            
            # Criar tipos de chave PIX
            tipos_pix = [
                dChave_PIX(descricao='CPF'),
                dChave_PIX(descricao='E-mail'),
                dChave_PIX(descricao='Celular'),
                dChave_PIX(descricao='Chave Aleatória')
            ]
            db.session.add_all(tipos_pix)
            
            # Criar bancos
            bancos = [
                dBancos(ID_BANCO=1, NOME_BANCO='SANTANDER', COD_BANCO='033'),
                dBancos(ID_BANCO=2, NOME_BANCO='BRADESCO', COD_BANCO='237'),
                dBancos(ID_BANCO=3, NOME_BANCO='CAIXA ECONOMICA FEDERAL', COD_BANCO='104'),
                dBancos(ID_BANCO=4, NOME_BANCO='BANCO DO BRASIL', COD_BANCO='001'),
                dBancos(ID_BANCO=5, NOME_BANCO='ITAU', COD_BANCO='341')
            ]
            db.session.add_all(bancos)
            
            # Criar 4 funcionários de exemplo
            funcionarios = [
                dFuncionarios(nome_funcionario='João Silva', salario_funcionario=5000.00),
                dFuncionarios(nome_funcionario='Maria Santos', salario_funcionario=4500.00),
                dFuncionarios(nome_funcionario='Pedro Oliveira', salario_funcionario=6000.00),
                dFuncionarios(nome_funcionario='Ana Costa', salario_funcionario=5500.00)
            ]
            db.session.add_all(funcionarios)
            
            db.session.commit()
            print("Banco de dados inicializado com sucesso!")
        
        # Popular dados financeiros se as tabelas estiverem vazias (independente de usuários)
        if dTipo_Lancamento.query.count() == 0:
            # Criar tipos de lançamento financeiro
            tipos_lancamento = [
                dTipo_Lancamento(descricao='Receita'),
                dTipo_Lancamento(descricao='Despesa'),
                dTipo_Lancamento(descricao='Investimento')
            ]
            db.session.add_all(tipos_lancamento)
            
            # Criar tipos de pagamento
            tipos_pagamento = [
                dTipo_Pagamento(descricao='Fatura/Prazo'),
                dTipo_Pagamento(descricao='Cartão de Crédito'),
                dTipo_Pagamento(descricao='A Vista'),
                dTipo_Pagamento(descricao='PIX'),
                dTipo_Pagamento(descricao='Transferência Bancária')
            ]
            db.session.add_all(tipos_pagamento)
            
            # Criar tipos de documentos
            tipos_documentos = [
                dDocumentos(descricao='Nota Fiscal de Serviço (NFS-e)'),
                dDocumentos(descricao='Recibo'),
                dDocumentos(descricao='Boleto'),
                dDocumentos(descricao='Contrato de Software'),
                dDocumentos(descricao='Fatura de Cloud'),
                dDocumentos(descricao='Sem Documento')
            ]
            db.session.add_all(tipos_documentos)
            
            # Criar centros de custos
            centros_custos = [
                dCentros_Custos(descricao='Administrativo'),
                dCentros_Custos(descricao='Comercial'),
                dCentros_Custos(descricao='Desenvolvimento Interno'),
                dCentros_Custos(descricao='Infraestrutura Cloud')
            ]
            db.session.add_all(centros_custos)
            
            # Criar contas macro
            contas_macro = [
                dContas(id_pai=None, nome='Infraestrutura e Cloud', tipo_dre='Custos'),
                dContas(id_pai=None, nome='Despesas Administrativas', tipo_dre='Despesas Operacionais'),
                dContas(id_pai=None, nome='Softwares e Assinaturas Internas', tipo_dre='Despesas Operacionais'),
                dContas(id_pai=None, nome='Despesas Bancárias', tipo_dre='Despesas Operacionais'),
                dContas(id_pai=None, nome='Despesas Com Pessoal', tipo_dre='Despesas Operacionais'),
                dContas(id_pai=None, nome='Equipamentos e Hardware', tipo_dre='Investimentos'),
                dContas(id_pai=None, nome='Impostos, Tributos e Taxas', tipo_dre='Despesas Operacionais'),
                dContas(id_pai=None, nome='Servicos Terceirizados', tipo_dre='Despesas Operacionais'),
                dContas(id_pai=None, nome='Alimentacao e Refeicoes', tipo_dre='Despesas Operacionais'),
                dContas(id_pai=None, nome='Viagens e Hospedagem', tipo_dre='Despesas Operacionais'),
                dContas(id_pai=None, nome='Receita Total', tipo_dre='Receita Bruta'),
                dContas(id_pai=None, nome='Investimento Total', tipo_dre='Investimentos'),
                dContas(id_pai=None, nome='Descontos Gerais', tipo_dre='Deducoes')
            ]
            db.session.add_all(contas_macro)
            db.session.flush()  # Flush para obter os IDs das contas macro
            
            # Criar subcontas (serão vinculadas após o flush)
            # Infraestrutura e Cloud
            conta_infra = dContas.query.filter_by(nome='Infraestrutura e Cloud').first()
            if conta_infra:
                subcontas_infra = [
                    dContas(id_pai=conta_infra.id, nome='Hospedagem de Servidores (AWS, Google Cloud, Azure)', tipo_dre='Custos'),
                    dContas(id_pai=conta_infra.id, nome='Banco de Dados em Nuvem', tipo_dre='Custos'),
                    dContas(id_pai=conta_infra.id, nome='Servicos de Email/SMTP', tipo_dre='Custos'),
                    dContas(id_pai=conta_infra.id, nome='Dominios e Certificados SSL', tipo_dre='Custos'),
                    dContas(id_pai=conta_infra.id, nome='APIs de Terceiros (OpenAI, Google Maps, etc)', tipo_dre='Custos')
                ]
                db.session.add_all(subcontas_infra)
            
            # Receita Total
            conta_receita = dContas.query.filter_by(nome='Receita Total').first()
            if conta_receita:
                subcontas_receita = [
                    dContas(id_pai=conta_receita.id, nome='Desenvolvimento de Software Sob Medida', tipo_dre='Receita Bruta'),
                    dContas(id_pai=conta_receita.id, nome='Licenciamento de ERP/SaaS', tipo_dre='Receita Bruta'),
                    dContas(id_pai=conta_receita.id, nome='Consultoria em Inovacao', tipo_dre='Receita Bruta'),
                    dContas(id_pai=conta_receita.id, nome='Suporte e Manutencao Mensal', tipo_dre='Receita Bruta')
                ]
                db.session.add_all(subcontas_receita)
            
            db.session.commit()
            print("Dados financeiros populados com sucesso!")

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
