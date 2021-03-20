# Este README serve para informações do projeto


## Virtualenv

#### Para baixar o virtualenv

> pip install virtualenv

#### Criar a pasta de ambiente virtual

> python -m venv env_seginfo / python3 -m venv env_seginfo

#### Para iniciar o ambiente virtual

> source /env_seginfo/bin/activate

#### Para finalizar o ambiente virtual

> source /env_seginfo/bin/deactivate


## Instalando dependências

> pip/pip3 install -r dev.txt

	Obs: Deve estar no mesmo diretório do arquivo --> /seg_info/requirements/dev.txt

#### Criando Banco PostgreSQL

> sudo -u postgres createdb seg_info_db

	Obs: Se o usuário do banco for diferente, será necessário alterar no arquivo de settings "dev.py"

#### Para aplicar as migrações

> python manage.py migrate --settings project.settings.dev


#### Para atualizar as migrações do projeto

> python manage.py makemigrations --settings project.settings.dev


#### Para rodar a aplicação

> python manage.py runserver --settings project.settings.dev


#### Para logar na aplicação será necessário um usuário primário

> python manage.py createsuperuser --settings project.settings.dev

	Obs: Assim aparecerá algumas perguntas no terminal/prompt de comando que respondendo será gerado um usuário super

	Exemplo:

	E-mail: administracao@portaria.com.br
	Nome: Administrador
	Senha: <senha>

