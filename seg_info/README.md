# Este README serve para informações do projeto


## Virtualenv

#### Para baixar o virtualenv

> pip install virtualenv

#### Criar um diretório para o ambiente virtual

> mkdir receitas_env

#### Gerar o virtual env dentro da pasta de receitas_env

> virtualenv receitas

>> Obs: se houver problema é possivel criar o ambiente virtual com o seguinte comando: python -m venv receitas / python3 -m venv receitas

#### Para iniciar o ambiente virtual

> source /receitas_env/receitas/bin/activate

#### Para finalizar o ambiente virtual

> source /receitas_env/receitas/bin/deactivate


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