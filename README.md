# Sistema de Cadastro de Funcionários e Dados Bancários

Aplicativo web para cadastro de funcionários e seus respectivos dados bancários para pagamento.

## Tecnologias Utilizadas

- Python 3.14+
- Flask 3.0.0
- Flask-SQLAlchemy 3.1.1
- SQLite
- Bootstrap 5.3.2
- jQuery 3.7.1

## Estrutura do Banco de Dados

### Tabelas

- **fUsuarios**: Usuários do sistema (login/senha)
- **dFuncionarios**: Cadastro de funcionários (id, nome, salário)
- **fDados_Bancarios**: Dados bancários dos funcionários
- **dTipo_Conta**: Tipos de conta (Corrente, Poupança)
- **dChave_PIX**: Tipos de chave PIX (CPF, E-mail, Celular, Chave Aleatória)

### Colunas de Auditoria

Todas as tabelas possuem as colunas:
- `CREATED_AT`: Data/hora de criação (UTC-3)
- `UPDATED_AT`: Data/hora de atualização (UTC-3)

## Instalação

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Execute o aplicativo:
```bash
python app.py
```

3. Acesse no navegador: `http://localhost:5000`

## Credenciais de Acesso

- **Usuário**: admin
- **Senha**: admin123

## Funcionalidades

### Tela de Login
- Autenticação de usuários cadastrados na tabela `fUsuarios`

### Aba Funcionários
- **Listar**: Visualização de todos os funcionários cadastrados
- **Cadastrar**: Novo funcionário com nome e salário (formato BRL)
- **Editar**: Alteração de dados do funcionário
- **Excluir**: Remoção de funcionário (cascata para dados bancários)
- **Visualizar**: Acesso aos detalhes do funcionário

### Dados Bancários
- **Modal de Cadastro**: Após cadastrar um funcionário, o sistema pergunta se deseja cadastrar os dados bancários "agora" ou "depois"
- **Campos**:
  - ID do Banco (ex: 001, 237, 341)
  - Tipo de Conta (Corrente/Poupança)
  - Nome do Titular
  - Tipo de Chave PIX (CPF, E-mail, Celular, Chave Aleatória)
  - Chave PIX

### CRUD Completo
- Criar, Ler, Atualizar e Excluir para funcionários e dados bancários

## Dados de Exemplo

O sistema é inicializado automaticamente com:
- 1 usuário admin (admin/admin123)
- 2 tipos de conta (Corrente, Poupança)
- 4 tipos de chave PIX
- 4 funcionários de exemplo com salários variados

## Formatação de Moeda

- O campo de salário utiliza máscara automática para formato BRL (R$ 1.234,56)
- O salário é armazenado como inteiro (centavos) para evitar problemas de precisão
- Exibição formatada automaticamente em toda a aplicação

## Timezone

Todas as datas/horas são registradas no timezone UTC-3 (America/Sao_Paulo)
