# Este README serve para informações do projeto

# Requisitos mínimos

	docker
	docker-compose

## Clonar o repositório

> git clone https://github.com/fabsvas/LGPD-SegurancaInformacao

# Rodando com Docker

## Renomeie o arquivo .env_example para .env

		PS. O arquivo .env normalmente está oculto na pasta do projeto.

## Fazer o build da imagem

	Estando no diretório que está o arquivo docker-compose:

		$ sudo docker-compose build

## Aplicação as migrações ao banco de dados 

	Estando no diretório que está o arquivo docker-compose:

		$ sudo docker-compose run --rm web python manage.py migrate

#### Para logar na aplicação será necessário um usuário primário

> sudo docker-compose run --rm web python manage.py createsuperuser --settings project.settings.dev

	Obs: Assim aparecerá algumas perguntas no terminal/prompt de comando que respondendo será gerado um usuário super

	Exemplo:

	E-mail: administracao@portaria.com.br
	Nome: Administrador
	Senha: <senha>

## Subindo a aplicação

	Estando no diretório que está o arquivo docker-compose:

		$ sudo docker-compose up

		ou

		$ sudo docker-compose run --rm --service-ports web (Esse caso é serve para debugar o código)
