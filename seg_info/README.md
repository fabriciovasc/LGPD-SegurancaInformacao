# Este README serve para informações do projeto


## Virtualenv

#### Para baixar o virtualenv

> pip install virtualenv

#### Acessar o diretório do projeto

> cd LGPD-SegurancaInformacao\seg_info

#### Criar um diretório para o ambiente virtual

> python -m venv receitas_env / python3 -m venv receitas_env

#### Para iniciar o ambiente virtual

> source /receitas_env/bin/activate

#### Para finalizar o ambiente virtual

> source /receitas_env/bin/deactivate


## Instalando dependências

> pip/pip3 install -r requirements.txt

>> Obs: Deve estar no mesmo diretório do arquivo

> Se tiver problemas com a biblioteca flask-mysqldb, é necessário instalar o seguinte:
	
	> sudo apt-get install python-dev default-libmysqlclient-dev libssl-dev 


#### Criando Banco MySQL
``` sql
$ mysql -u root

mysql> CREATE USER 'dt_admin'@'localhost' IDENTIFIED BY 'admin2021';

mysql> CREATE DATABASE seginfo_db;

mysql> GRANT ALL PRIVILEGES ON seginfo_db . * TO 'dt_admin'@'localhost';
```

#### Qualquer dúvida sobre o flask-script

> python manage.py db  --help

#### Para iniciar as migrações do projeto

> python manage.py db init


#### Para atualizar as migrações do projeto

> python manage.py db revision


#### Para aplicar as migrações (após ter criado o banco)

> python manage.py db migrate 


#### Para rodar a aplicação

> python manage.py runserver
