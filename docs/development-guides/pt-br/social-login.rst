==============================
Login utilizando redes sociais
==============================

Além do formulário de registro, usuários podem entrar na EJ com sua conta Google. Para isso, é necessário configurar o app social no painel do Django.

Google
======

Para permitir login via conta do Google, é necessário um domínio de primeiro nível válido em que você possa confirmar a propriedade. Vá para a interface de administração de aplicativos (https://console.developers.google.com/) e crie um projeto. Crie uma nova credencial e adicione https://your-host/accounts/google/login/callback/ como URI de redirecionamento autorizada. Lembre-se também de adicionar o domínio como um domínio válido.

Agora, no Django, vá para a interface de administração e crie um novo aplicativo social: http://localhost:8000/admin/socialaccount/socialapp/add/. Escolha o provedor "Google", coloque um nome tipo "EJ Google", escolha o site ejplatform.org.br e coloque o id do aplicativo no campo "Client id" e a chave secreta do aplicativo no campo "Secret key". Você pode encontrar ambos na página do aplicativo do Google, em Credenciais.

Outras informações
==================

Para todos os casos, para desenvolvimento local, você pode também precisar definir, em src/ej/settings/__init__.py, ACCOUNT_EMAIL_VERIFICATION = 'none'.

Mais detalhes em https://django-allauth.readthedocs.io/en/latest/providers.html.
