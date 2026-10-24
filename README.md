# Simulador de Batalhas Pokémon RPG

Um programa para ajudar a organizar as batalhas do seu RPG de mesa de Pokémon. A ideia é inspirada nos jogos oficiais, mas usa regras próprias para atributos, progressão e habilidades. Não é uma cópia do sistema oficial.

Este README descreve as regras e o funcionamento desejado do projeto. Os custos da árvore, os pontos recebidos por nível e alguns detalhes das mecânicas especiais ainda serão definidos.

## O que o programa deverá fazer

- Cadastrar Pokémon, seus atributos, tipos e golpes.
- Deixar os jogadores escolherem golpes durante a batalha.
- Calcular dano e aplicar os efeitos dos golpes.
- Administrar itens e mecânicas especiais.
- Permitir que os Pokémon desbloqueiem melhorias numa árvore de habilidades.
- Deixar os dados de Pokémon e golpes separados das regras que executam a batalha, para que seja possível adicionar conteúdo sem reescrever o funcionamento do programa.

## O que já foi ajustado no protótipo

- O cálculo de dano em `batalha.py` segue a fórmula personalizada deste RPG, usa um fator sorteado entre `0,95` e `1,05` uma vez por ataque e não aplica STAB nem crítico.
- O fator de status começa em `1,0` (neutro), pois os demais modificadores ainda não foram definidos. A regra provisória para dano inteiro é descartar a parte decimal.
- A tabela dos 18 tipos fica em `type_chart.py`; os dados dos golpes ficam em `golpes_lib.py`.
- Antes da batalha, cada jogador escolhe manualmente até três golpes disponíveis para cada Pokémon; Proteção é incluída além deles.
- O programa agora abre com a tela de título **POKÉMON: O RPG** e um menu de terminal para batalhar, cadastrar/ver Pokémon e itens, ajustar tamanhos ou sair.
- As batalhas permitem escolher 1x1, 2x2 ou 3x3 Pokémon ativos por lado. Cada treinador monta uma equipe de três; Pokémon que não começam no campo ficam na reserva.
- Cada Pokémon tem um porte, que pode ser Pequeno, Médio, Grande, Gigante ou qualquer rótulo personalizado. Esse dado fica separado da lógica de combate para uso futuro com sprites.
- Um golpe mencionado nos dados de um Pokémon, mas ainda não cadastrado em `golpes_lib.py`, agora gera uma mensagem de erro em vez de receber um golpe genérico silenciosamente.

O protótipo continua sendo executado no terminal. A interface gráfica, árvore de habilidades, aplicação de efeitos de itens e mecânicas especiais ainda não foram implementadas.

## Regras dos atributos

### Atributos não aumentam automaticamente com o nível

Os atributos de combate ficam fixos quando são definidos. Subir de nível não aumenta esses valores sozinho. O nível serve para a progressão e para liberar opções na árvore de habilidades.

Os seis atributos básicos são:

- HP
- Ataque
- Defesa
- Ataque Especial
- Defesa Especial
- Velocidade

Os valores serão baseados nos atributos padrão dos jogos oficiais no nível 50. Primeiro, o valor será arredondado para o múltiplo de 5 mais próximo. Depois, será dividido por 10 para ser mostrado.

**Exemplo:** `77 → 75 → 7,5`.

Os valores exatos e o método definitivo de arredondamento ainda poderão ser ajustados. Depois de definidos para um Pokémon, os atributos não mudam automaticamente quando ele sobe de nível.

## Níveis e árvore de habilidades

Subir de nível dá acesso à progressão, mas não libera tudo automaticamente. O treinador escolhe em que investir, usando a árvore de habilidades do Pokémon.

A árvore poderá ter desbloqueios destas categorias:

- **Afeto:** melhorias ligadas ao vínculo entre o Pokémon e seu treinador.
- **Força:** melhorias nos seis atributos básicos. Ataque e Ataque Especial melhoram juntos; Defesa e Defesa Especial também melhoram juntas. HP e Velocidade são as outras duas melhorias, formando quatro tipos de melhoria de atributo.
- **Golpes:** desbloqueia novos golpes e mais espaços para usá-los.
- **Mega Evolução:** libera a possibilidade de Mega Evoluir.
- **Terastalização:** libera a mecânica de Terastalização.
- **Gigantamax:** libera a possibilidade de Gigantamax.
- **Movimento Z:** libera a possibilidade de usar um Movimento Z.

### Custos e requisitos

Cada habilidade poderá ter seu próprio custo. Em geral, desbloqueios mais poderosos devem exigir mais investimento.

Além do custo, um desbloqueio poderá exigir:

- nível mínimo;
- nível mínimo ou máximo de Afeto;
- outra habilidade já desbloqueada;
- outras condições especiais definidas para aquela habilidade.

A quantidade de pontos recebidos por nível, os custos e a estrutura completa da árvore ainda serão definidos. A árvore deverá ser configurável para permitir adicionar ou ajustar habilidades e requisitos sem alterar o código que executa a batalha.

### Escolhas e reembolso

Mesmo no nível máximo (50), não deverá ser possível comprar todas as melhorias. O treinador terá que escolher uma estratégia para cada Pokémon.

As melhorias compradas poderão ser reembolsadas. Assim, o treinador poderá recuperar o investimento e escolher outro caminho na árvore. A regra exata do reembolso ainda será definida.

## Sistema de golpes

Os dados dos golpes devem ficar separados do código de batalha. Assim, um novo golpe poderá ser cadastrado sem reescrever o sistema que calcula e resolve os turnos.

Cada Pokémon terá nove golpes principais anotados pelo treinador:

- três golpes físicos;
- três golpes especiais;
- três golpes de status.

Além desses nove, todos os Pokémon terão **Proteção** como o décimo golpe. Apesar de conhecer os nove golpes principais e Proteção, cada Pokémon só poderá levar para a batalha três dos nove golpes principais. Com Proteção, poderá usar até quatro golpes na batalha.

Cada golpe poderá guardar informações como:

- nome;
- tipo;
- categoria (físico, especial ou status);
- poder;
- outros efeitos que forem implementados.

Golpes de status poderão ter efeitos em vez de causar dano direto, conforme os dados cadastrados para cada golpe.

O sistema deverá permitir cadastrar golpes novos como dados, sem criar uma função exclusiva para cada golpe. Golpes comuns devem usar o comportamento geral definido pelos seus dados. Se um golpe tiver um efeito especial que não caiba nesse comportamento geral, ele poderá receber uma funcionalidade própria sem obrigar a reescrever o restante do sistema.

## Cálculo do dano

O dano será calculado automaticamente usando esta fórmula:

```text
(((att ÷ def) × poder × 22) ÷ 50 + 2)
× efetividade dos tipos
× fator aleatório
× modificador de status
```

As operações devem acontecer nesta ordem:

1. Dividir o ataque pela defesa.
2. Multiplicar o resultado pelo poder do golpe e por 22.
3. Dividir por 50.
4. Somar 2.
5. Multiplicar pela efetividade dos tipos.
6. Multiplicar pelo fator aleatório.
7. Multiplicar pelo modificador de status.

O fator aleatório deverá ser sorteado a cada cálculo dentro do intervalo definido. O intervalo inicial descrito para esta regra é de `0,95` a `1,05`. A fórmula é própria deste RPG: não deve ser substituída pela fórmula oficial dos jogos Pokémon.

Para golpes especiais, o cálculo deverá usar Ataque Especial e Defesa Especial no lugar de Ataque e Defesa. O significado e os valores dos modificadores de status e da efetividade dos tipos deverão seguir as regras próprias deste RPG quando forem definidos. O arredondamento do dano final deverá ser sempre consistente; a regra poderá ser ajustada quando for decidida.

## Tabela de efetividade dos tipos

O sistema deverá ter uma tabela de efetividade separada da lógica da batalha, para que seja fácil conferir e alterar seus dados. A tabela oficial dos 18 tipos de Pokémon será a referência inicial e deverá cobrir:

- dano super efetivo;
- dano pouco efetivo;
- dano neutro;
- imunidades;
- Pokémon com um ou dois tipos defensivos.

Contra um Pokémon de dois tipos, o programa deverá multiplicar os dois fatores de efetividade. Por exemplo, se um golpe for super efetivo contra os dois tipos, os dois multiplicadores se combinam para calcular a efetividade total.

## Cadastro e dados de Pokémon

Os dados de cada Pokémon deverão ficar separados da lógica que executa a batalha. Sempre que possível, será possível cadastrar Pokémon copiando e colando dados em um formato definido pelo projeto, em vez de programar cada espécie. A escolha de quais golpes o Pokémon leva para a batalha continuará sendo manual.

Um registro poderá incluir:

- nome da espécie e tipos;
- atributos fixos e HP máximo;
- habilidades;
- golpes disponíveis;
- informações necessárias para transformações;
- dados específicos usados pela árvore de habilidades.

Adicionar uma espécie nova deverá ser um processo simples e previsível. Os dados específicos não deverão ficar espalhados pelo código principal.

No menu, a opção **Cadastrar Pokémon** aceita um objeto JSON ou uma lista de objetos colada no terminal. Cada registro precisa conter espécie, nome, nível, dois campos de tipo, HP, Ataque, Defesa, Ataque Especial, Defesa Especial e Velocidade. Os campos de golpes são opcionais e cada golpe informado precisa existir em `golpes_lib.py`. `tamanho` também é opcional; se não for informado, começa como `Médio`.

Exemplo de registro:

```json
{
  "espécie": "Meu Pokémon",
  "nome": "Meu Pokémon",
  "nível": "10",
  "tipo 1": "Fogo",
  "tipo 2": "Nenhum",
  "habilidade": "Habilidade de exemplo",
  "fis. ataque 1": "brasas",
  "fis. ataque 2": "",
  "fis. ataque 3": "",
  "sp. ataque 4": "",
  "sp. ataque 5": "",
  "sp. ataque 6": "",
  "stat. ataque 7": "",
  "stat. ataque 8": "",
  "stat. ataque 9": "",
  "hp": 50,
  "att": 5,
  "def": 5,
  "sp.att": 5,
  "sp.def": 5,
  "speed": 5,
  "tamanho": "Médio"
}
```

Cole o objeto (ou uma lista `[...]`) e finalize com uma linha vazia. O cadastro é salvo em `pokemon_custom.json`. Os tamanhos personalizados escolhidos pelo menu ficam em `pokemon_tamanhos.json`; os dados iniciais de tamanho também aparecem em cada registro de `pokémon_lib.py`.

## Tamanho e sprites futuros

O campo `tamanho` registra o porte do Pokémon sem alterar seus atributos nem o cálculo de dano. No menu, é possível escolher **Pequeno**, **Médio**, **Grande**, **Gigante** ou escrever outro nome. Assim, seus portes podem ser personalizados agora e associados a sprites ou escalas visuais quando essa parte for desenvolvida. O protótipo ainda não mostra sprites nem aplica escala de imagem.

## Menu e formatos de batalha

Ao iniciar `batalha.py`, aparece a tela de título **POKÉMON: O RPG** e estas opções:

1. Iniciar batalha.
2. Cadastrar Pokémon colando dados JSON.
3. Ver Pokémon cadastrados.
4. Cadastrar item.
5. Ver itens cadastrados.
6. Ajustar o tamanho de um Pokémon.
7. Sair.

Ao iniciar uma luta, o mestre escolhe quantos Pokémon ficam em campo ao mesmo tempo: **1x1, 2x2 ou 3x3**. Cada treinador ainda monta uma equipe de três Pokémon; os primeiros selecionados começam em campo até preencher o formato escolhido e os restantes ficam na reserva. Cada Pokémon em campo escolhe sua ação e, para golpes que miram o oponente, o alvo. Se houver um desmaio e uma vaga, o treinador escolhe um substituto da reserva. Em formatos com menos de três Pokémon ativos, também é possível trocar um Pokémon em campo por um da reserva usando uma ação.

Itens cadastrados são salvos em `itens.json` com nome e descrição. O cadastro serve para organizar os itens do RPG: seus efeitos ainda não são aplicados durante a batalha.

## Interface gráfica

O programa deverá ter uma interface gráfica simples e organizada, pensada para consulta rápida durante uma sessão de RPG. A prioridade é deixar as informações fáceis de ler, não mostrar uma representação visual dos Pokémon.

Por enquanto, a interface de batalha não deverá usar sprites, desenhos ou imagens de Pokémon. A organização deverá permitir que sprites criados pelo usuário possam ser adicionados no futuro, sem que eles sejam necessários para o funcionamento atual.

Conforme as funcionalidades forem implementadas, a interface deverá poder mostrar:

- nome e tipos do Pokémon;
- HP atual e máximo;
- poder dos golpes e golpes disponíveis;
- dano causado;
- estados e modificadores ativos;
- informações relevantes da batalha;
- registro das ações realizadas.

O objetivo é ajudar o mestre a consultar rapidamente o que está acontecendo, sem precisar parar a sessão para fazer as contas manualmente.

## Estados, modificadores e efeitos de batalha

O sistema deverá ser preparado para controlar efeitos positivos e negativos, incluindo:

- modificadores temporários de atributos;
- efeitos causados por golpes;
- alterações de forma;
- efeitos que durem por um período determinado;
- outros efeitos personalizados.

Os efeitos deverão ser organizados de forma modular. Adicionar um efeito novo não deverá exigir reescrever toda a calculadora de dano. A lista final de estados e as regras de duração ainda serão definidas.

## Itens

Os itens terão um sistema próprio, separado da árvore de habilidades. Não haverá árvore para desbloquear itens. Seus tipos, efeitos e restrições deverão ser fáceis de modificar.

O sistema de itens será mais simples e menos extenso do que os sistemas de habilidades e transformações. Os efeitos e limites de uso ainda serão especificados.

## Transformações e mecânicas especiais

Mega Evolução, Terastalização e Gigantamax deverão estar disponíveis como possibilidades de progressão e combate. O acesso dependerá de desbloqueios na árvore, e custos e requisitos poderão variar de acordo com o Pokémon e a mecânica.

O sistema deverá permitir diferenças entre Pokémon, incluindo formas e alterações específicas. Movimentos Z também estão previstos como desbloqueio da árvore. As regras detalhadas de cada mecânica ainda serão definidas.

## Organização do programa

Para facilitar a manutenção, o projeto deverá separar, sempre que possível:

- dados de Pokémon;
- dados de golpes;
- tabela de tipos;
- cálculo de dano;
- estado atual da batalha;
- sistema de progressão;
- sistema de itens;
- mecânicas especiais;
- interface gráfica.

Essa separação ajuda a adicionar dados e funcionalidades sem duplicar código ou concentrar tudo em funções gigantes. As entradas deverão ser validadas e erros comuns, como divisão por zero, deverão ser tratados de forma clara.

## Etapas de desenvolvimento

O sistema poderá ser construído aos poucos, priorizando uma versão pequena que funcione antes de acrescentar todas as mecânicas:

1. Calculadora de dano com a fórmula personalizada.
2. Tabela completa de efetividade dos tipos.
3. Cadastro de Pokémon e golpes.
4. Controle de HP e registro de dano.
5. Sistema de batalha por turnos.
6. Estados e modificadores.
7. Interface gráfica mais completa.
8. Sistema de progressão e árvore de habilidades.
9. Sistema de itens.
10. Mega Evolução, Terastalização, Gigantamax e outras mecânicas especiais.
11. Salvamento e carregamento dos dados.
12. Testes e correção de erros.

Durante o desenvolvimento, as partes importantes deverão ser explicadas de forma acessível, com instruções de qual arquivo editar e como executar e testar cada etapa. Regras já estabelecidas não deverão ser alteradas sem autorização.

Não se deve inventar custos, requisitos ou mecânicas personalizadas sem identificá-los claramente como provisórios. Se uma regra necessária ainda não tiver sido definida, deve-se perguntar antes de implementá-la ou usar uma configuração provisória claramente marcada.

## Fluxo de uma batalha

O fluxo abaixo descreve a batalha desejada, em linguagem simples:

1. **Preparar os participantes:** o programa identifica os treinadores e os Pokémon que participarão do combate.
2. **Preparar os Pokémon:** cada Pokémon entra com seus atributos fixos, nível, habilidades desbloqueadas, itens e golpes escolhidos.
3. **Começar o combate:** os Pokémon escolhidos entram em campo e o programa mostra as informações importantes para os jogadores.
4. **Escolher uma ação:** no turno, o jogador seleciona um golpe disponível ou outra ação permitida pelas regras.
5. **Verificar condições:** o programa confere se o Pokémon pode agir e se há efeitos, itens ou mecânicas especiais que alterem a ação.
6. **Resolver o golpe:** se for um golpe que causa dano, o programa aplica a fórmula, os modificadores e os efeitos correspondentes. Golpes de status aplicam seus efeitos definidos.
7. **Atualizar a batalha:** o HP e os demais estados dos Pokémon são atualizados, e o programa mostra o resultado aos jogadores.
8. **Continuar os turnos:** os jogadores continuam escolhendo ações até a batalha terminar conforme as regras do RPG.
9. **Encerrar o combate:** o programa registra o resultado e deixa os jogadores administrarem o que vem depois, como itens ou progressão, quando essas funções estiverem disponíveis.

Algumas regras de batalha — por exemplo, a ordem de ação, a troca de Pokémon e as condições exatas de vitória — ainda precisam ser definidas pelo RPG. O programa deverá permitir que essas regras sejam administradas sem confundi-las com os dados dos Pokémon e dos golpes.

## Mecânicas especiais e itens

O programa deverá permitir administrar Mega Evolução, Terastalização, Gigantamax e Movimentos Z. Cada Pokémon só poderá usar uma mecânica especial se tiver desbloqueado essa possibilidade na sua árvore e se cumprir as regras específicas do RPG.

Os itens também deverão ser gerenciados pelo programa. Seus efeitos, limites de uso e regras de obtenção ainda serão especificados. Assim como os golpes, os itens deverão ser cadastrados como dados sempre que possível, sem exigir mudanças no núcleo do sistema de batalha.

## Configurabilidade e novos conteúdos

Pokémon, golpes, habilidades e itens devem ser tratados como dados que o programa lê. O objetivo é que seja possível cadastrar novos conteúdos e ajustar custos ou requisitos sem reescrever a lógica principal da batalha.

As regras que ainda dependem de decisão — como custos da árvore, pontos por nível, valores exatos dos atributos, efeitos dos itens e funcionamento detalhado das mecânicas especiais — devem poder ser ajustadas conforme o RPG evoluir.

## Estado atual do projeto

O código existente é um protótipo simples de batalha no terminal. Ele já calcula o dano pela fórmula personalizada, usa a tabela de tipos externa e permite escolher os golpes antes da batalha. Ainda não implementa todo o sistema descrito neste documento, incluindo interface gráfica, árvore de habilidades, gerenciamento completo de itens, salvamento e mecânicas especiais.

Para abrir o menu do protótipo atual, abra um terminal na pasta do projeto e rode:

```bash
python batalha.py
```

No Windows, também é possível usar o Python do ambiente virtual do projeto:

```powershell
.\.venv\Scripts\python.exe batalha.py
```

O protótipo carrega os dados de Pokémon de `pokémon_lib.py`, os dados de golpes de `golpes_lib.py` e a tabela de efetividade de `type_chart.py`. Esses arquivos devem permanecer na mesma pasta de `batalha.py`. Para rodar os testes automatizados da calculadora e da tabela de tipos:

```powershell
.\.venv\Scripts\python.exe -m unittest test_batalha
```
#   P r o j e t o - d e - b a t l h a - p o k e m o n  
 