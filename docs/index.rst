Bem vinda à documentação da Empurrando Juntas.
===============================================

A Empurrando Juntas (EJ) é uma plataforma de coleta de opinião multicanal,
que permite construir grupos de opinião a partir da modelagem de personas.
Os usuários participam em conversas, votando em comentários existentes e
adicionando novos comentários para enriquecer a discussão.

Cada comentário pode possui três opções de voto: concordar, discordar e pular.
Conforme os usuários participam de uma conversa, o algorítmo de clusterização
posiciona cada participante em um *cluster*. Um cluster representa um conjunto
de usuários que votam de forma aproximada às personas modeladas para a conversa.

.. note::

   Uma persona representa um participante imaginário, que vota nos comentários
   de determinada forma. O administrador pode definir personas depois de cadastrar
   uma nova conversa.

.. figure:: user-guides/images/bubbles.png
   :align: center

   Grupos de opinião de uma conversa


Dizer que a EJ é multicanal significa que existe mais de uma forma de participar
de uma conversa. A tabela a seguir lista quais possibilidades o administrador de
uma conversa tem para disponibilizar uma conversa ao público:

.. csv-table:: Opções de multicanal
   :header: "Canal", "Descrição"

   "Página da conversa", "Modo convencional de participação. O usuário acessa a página da conversa na plataforma web e participa."
   "Componente de opinião", "Componente Web integrado à API da EJ, que permite participar de uma conversa a partir de uma página html."
   "Bot de enquetes", "Bot que converte uma conversa da EJ para uma enquete do Telegram. Pode ser utilizado em grupos e canais."
   "Bot opinião", "Bot que simula uma conversa com o usuário e permite votar e adicionar comentários."
   "Template de email", "Arquivo HTML que simula a página da conversa. Esse arquivo pode ser utilizado em campanhas de email."



Além dos canais de participação, a EJ também disponibiliza uma conjunto de relatórios que
permitem avaliar a performance dos comentários e dos grupos de opinião. É possível exportar
os dados coletados para integração com outras ferramentas como Mautic, PowerBI e Excel.

.. note::

    O objetivo deste guia é auxiliar pessoas interessadas em realizar projetos de escuta
    e participação social a adotaram a EJ como uma solução viável para entender o que
    determinado público pensa sobre determinado assunto e, a partir desse entendimento,
    melhorar suas iniciativas de comunicação e ativações pós-coleta.


.. toctree::
   :caption: Guia de desenvolvimento
   :maxdepth: 2

   development-guides/pt-br/index

.. toctree::
   :caption: Guia de usuário
   :maxdepth: 2

   user-guides/pt-br/index
