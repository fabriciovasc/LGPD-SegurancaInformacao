# Este README serve para informações do projeto


## Clonar o repositório

> git clone https://github.com/fabsvas/LGPD-SegurancaInformacao

# Acessar a pasta do repositório

> cd LGPD-SegurancaInformacao/seg_info

## Virtualenv

#### Para baixar o virtualenv

> pip install virtualenv

#### Criar a pasta de ambiente virtual

> python -m venv env_seginfo / python3 -m venv env_seginfo

#### Para iniciar o ambiente virtual

> source /env_seginfo/Scripts/activate  - No windows
> 
> source /env_seginfo/bin/activate  - No Linux

#### Para finalizar o ambiente virtual

> source /env_seginfo/Scripts/deactivate - No windows
> 
> source /env_seginfo/bin/deactivate - No Linux


## Instalando dependências

> pip/pip3 install -r requirements/dev.txt

	

#### Criando Banco PostgreSQL

> sudo -u postgres createdb seg_info_db

	Obs: Se o usuário do banco for diferente, será necessário alterar no arquivo de settings "dev.py"

#### Para aplicar as migrações

> python manage.py migrate --settings project.settings.dev


#### Para atualizar as migrações do projeto

> python manage.py makemigrations --settings project.settings.dev

#### Para logar na aplicação será necessário um usuário primário

> python manage.py createsuperuser --settings project.settings.dev

	Obs: Assim aparecerá algumas perguntas no terminal/prompt de comando que respondendo será gerado um usuário super

	Exemplo:

	E-mail: administracao@portaria.com.br
	Nome: Administrador
	Senha: <senha>

#### Para rodar a aplicação

> python manage.py runserver --settings project.settings.dev
