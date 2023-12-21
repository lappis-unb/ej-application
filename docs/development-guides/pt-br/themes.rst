******
Temas
******

É possível implementar temas customizados para a plataforma. O tema padrão
é versionado no app **ej**, no diretório **ej/static/ej/**.
A EJ irá carregar o tema a partir da variável de ambiente **EJ_THEME**. O
valor dessa variável precisa ser o nome do app responsável por armazenar
o tema.

.. note::

    Uma vez criado o app responsável pelo tema e definida a variável
    EJ_THEME, os scripts de compilação irão procurar os arquivos estáticos
    dentro do diretório <theme_app>/static/<theme_app>.

Por ser um app Django, você será capaz de customizar não só o tema, mas
também os templates jinja2, models e views. Um exemplo de implementação de
tema para a EJ seguindo esta estrutura, pode ser encontrado
`neste repositório <https://gitlab.com/pencillabs/itsrio/ej-application/>`_.

.. note::

    Você pode começar a implementação de um tema customizado, copiando os arquivos do
    tema padrão para o seu app, mas mantendo a estrutura de diretórios estáticos.
