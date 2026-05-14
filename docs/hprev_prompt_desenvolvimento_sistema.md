# Prompt detalhado para desenvolvimento do sistema HPrev

Use o texto abaixo como prompt para solicitar a implementacao do sistema.

```text
Voce deve desenvolver o sistema web HPrev para cadastro, edicao, visualizacao e manutencao de histogramas de mao de obra e equipamentos.

## 1. Objetivo do sistema

Criar um sistema web para permitir:

- Cadastro de histogramas.
- Cadastro de fases dentro de cada histograma.
- Cadastro de secoes de recursos dentro de cada histograma.
- Cadastro de recursos dentro de cada secao.
- Cadastro de colunas customizaveis de atributos dos recursos.
- Cadastro/edicao de quantitativos diarios por recurso dentro do periodo do histograma.
- Visualizacao do histograma em formato de tabela, com cabecalho temporal, secoes, recursos, totais parciais por secao e total geral por dia.

O histograma deve funcionar como uma tabela operacional na qual a parte esquerda identifica recursos e atributos, e a parte direita contem as quantidades de cada recurso por dia exibido.

## 2. Stack obrigatoria e requisitos nao funcionais

### 2.1 Frontend

- O sistema deve ser web.
- Usar ReactJS.
- Usar boilerplate Vite com TypeScript.
- Usar Tailwind CSS para toda a estilizacao.
- Usar react-hook-form nos formularios.
- Os formularios devem ser uncontrolled, usando os recursos nativos do react-hook-form sempre que possivel.
- Usar Zod para validacao dos formularios.
- Integrar Zod com react-hook-form por meio de resolver apropriado.
- Evitar formularios controlados quando nao houver necessidade real.

### 2.2 Tabela do histograma

- A tabela deve possuir rolagem para a area de linhas.
- Os headers da tabela devem permanecer fixos durante a rolagem vertical.
- A parte esquerda com identificacao dos recursos deve permanecer alinhada com a parte direita de quantitativos.
- A implementacao deve preservar a legibilidade em periodos longos.
- As linhas da tabela devem ser virtualizadas durante a rolagem para evitar sobrecarga de renderizacao.
- Usar uma biblioteca de virtualizacao adequada, por exemplo TanStack Virtual ou equivalente.
- A rolagem horizontal deve permitir navegar pelos dias do histograma sem perder os headers.
- Recomenda-se manter as colunas fixas da esquerda como sticky.
- Recomenda-se manter os headers superiores como sticky.
- Se o numero de dias puder ser muito grande, avaliar tambem virtualizacao horizontal de colunas de dias, mas o requisito obrigatorio inicial e virtualizacao das linhas.

### 2.3 Backend e persistencia

- O backend deve ser desenvolvido em Python.
- Utilizar FastAPI para a API HTTP.
- Utilizar SQLAlchemy como ORM.
- Utilizar Alembic para migrations do banco de dados.
- Utilizar driver SQL Server compativel com SQLAlchemy, preferencialmente `pyodbc` com ODBC Driver 18.
- O banco de dados inicial sera Microsoft SQL Server.
- Em desenvolvimento, o SQL Server deve ser dockerizado.
- Criar configuracao Docker/Docker Compose para subir o SQL Server em ambiente local de desenvolvimento.
- Incluir arquivo `.env.example` com variaveis necessarias para preenchimento das credenciais do banco.
- Criar arquivo `.env` de exemplo para desenvolvimento local se o padrao do projeto permitir, sem versionar segredos reais.
- Variaveis esperadas:
  - `DATABASE_URL`
  - `SQLSERVER_HOST`
  - `SQLSERVER_PORT`
  - `SQLSERVER_DATABASE`
  - `SQLSERVER_USER`
  - `SQLSERVER_PASSWORD`
  - `SQLSERVER_SA_PASSWORD`
  - `APP_PORT`
  - `VITE_API_BASE_URL`
- `DATABASE_URL` deve usar formato compativel com SQLAlchemy para SQL Server, por exemplo `mssql+pyodbc://...`.
- Nao hardcodar credenciais de banco no codigo.
- Preparar migrations Alembic.
- Usar Pydantic/FastAPI para schemas de entrada e saida da API.

### 2.4 Arquitetura sugerida

Como o acesso ao banco deve ficar no backend, implemente uma arquitetura com:

- Frontend React/Vite/TypeScript.
- Backend Python/FastAPI com API HTTP.
- SQLAlchemy no backend.
- Alembic para migrations.
- SQL Server como banco.
- Docker Compose para SQL Server em dev.
- Scripts de desenvolvimento para subir frontend, backend e banco.

Estruture o backend de forma simples e consistente, separando rotas, schemas Pydantic, modelos SQLAlchemy, camada de servico/regras de negocio e configuracao de banco.

## 3. Entidades principais

### 3.1 Histograma

Campos:

- `id`
- `name`
- `description`
- `startDate`
- `endDate`
- `stepDays`
- `createdAt`
- `updatedAt`

Regras:

- `name` e obrigatorio.
- `name` deve ser unico no sistema.
- `description` e opcional e deve ser exibida como subtitulo.
- `startDate` e obrigatoria.
- `endDate` e obrigatoria.
- `endDate` deve ser maior ou igual a `startDate`.
- `stepDays` e obrigatorio.
- `stepDays` deve ser inteiro positivo.
- `stepDays` define de quantos em quantos dias as colunas de dias serao exibidas no histograma.

### 3.2 Fase do projeto

Campos:

- `id`
- `histogramId`
- `name`
- `startDate`
- `endDate`
- `order`
- `createdAt`
- `updatedAt`

Regras:

- Uma fase sempre pertence a um histograma.
- `name` e obrigatorio.
- `name` deve ser unico dentro do escopo de um histograma.
- `startDate` e `endDate` devem estar dentro do periodo do histograma.
- `endDate` deve ser maior ou igual a `startDate`.
- Fases de um mesmo histograma nao podem se sobrepor.
- A validacao de sobreposicao deve acontecer no backend antes de persistir.
- A tela deve exibir feedback claro quando houver tentativa de criar fase fora do periodo ou sobreposta.

### 3.3 Secao de recursos

Campos:

- `id`
- `histogramId`
- `name`
- `colorHex`
- `order`
- `createdAt`
- `updatedAt`

Regras:

- Uma secao sempre pertence a um histograma.
- `name` e obrigatorio.
- Recomenda-se que `name` seja unico dentro do escopo de um histograma.
- `colorHex` e obrigatorio.
- `colorHex` deve aceitar uma cor customizada pelo usuario em formato hexadecimal, por exemplo `#0F766E`.
- Cada secao deve usar sua propria cor de fundo no header da secao.
- O usuario deve conseguir customizar a cor da secao ao criar ou editar a secao.
- A cor do header da secao deve ser aplicada na tabela do histograma.
- Deve existir uma linha de total parcial para cada secao, logo apos os recursos daquela secao.

### 3.4 Coluna customizavel de recurso

Campos:

- `id`
- `histogramId`
- `name`
- `type`
- `required`
- `options`
- `order`
- `createdAt`
- `updatedAt`

Tipos permitidos:

- `string`: aceita texto ou numero livre como string.
- `dropdown`: permite selecionar um valor de uma lista pre-definida pelo usuario.
- `tags`: permite informar multiplas tags.

Regras:

- As colunas customizaveis pertencem ao histograma.
- `name` e obrigatorio.
- `name` deve ser unico dentro do escopo do histograma.
- `type` e obrigatorio.
- Para `dropdown`, o usuario deve informar uma lista de opcoes.
- Para `tags`, armazenar lista de valores.
- O usuario pode adicionar e remover colunas customizaveis.
- A coluna fixa "Nome do recurso" nao pode ser removida, renomeada ou transformada em coluna customizavel.

### 3.5 Recurso

Campos:

- `id`
- `histogramId`
- `sectionId`
- `name`
- `order`
- `createdAt`
- `updatedAt`

Regras:

- Um recurso sempre pertence a uma secao.
- Um recurso tambem deve pertencer ao histograma da secao.
- `name` e obrigatorio.
- A coluna "Nome do recurso" e fixa, obrigatoria e nao editavel como definicao de coluna.
- O usuario deve conseguir adicionar recursos dentro de uma secao.
- Se nao existir nenhuma secao cadastrada, ao clicar no botao de adicionar recurso, o sistema deve primeiro solicitar o cadastro da secao.
- Se ja existir secao cadastrada, o botao `+` deve aparecer no canto direito do header de cada secao para adicionar recurso naquela secao.

### 3.6 Valor de atributo customizado do recurso

Campos:

- `id`
- `resourceId`
- `customColumnId`
- `value`

Regras:

- Armazena o valor de cada coluna customizada para cada recurso.
- Para colunas `dropdown`, validar se o valor pertence as opcoes cadastradas.
- Para colunas `tags`, armazenar como JSON/lista ou tabela relacional, conforme melhor modelagem com SQLAlchemy e SQL Server.
- Para colunas `string`, aceitar texto livre.

### 3.7 Quantitativo diario do recurso

Campos:

- `id`
- `resourceId`
- `date`
- `quantity`
- `createdAt`
- `updatedAt`

Regras:

- `date` deve estar dentro do periodo do histograma.
- `quantity` deve ser numerico e nao negativo.
- Recomenda-se permitir quantidade decimal para equipamentos e mao de obra fracionada, salvo se houver decisao de negocio por inteiro.
- Deve existir no maximo um quantitativo por recurso e data.
- A tabela deve permitir edicao dos quantitativos por recurso/dia.
- Dias de fim de semana devem ter fundo levemente diferente.

## 4. Formulario de cadastro/edicao do histograma

Campos:

- Nome do histograma.
- Descricao do histograma.
- Data de inicio.
- Data de termino.
- Step em dias.
- Fases do projeto.
- Secoes de recursos, incluindo nome, ordem e cor customizada.
- Colunas customizaveis dos recursos.

Comportamento:

- Usar react-hook-form uncontrolled.
- Usar Zod para schema de validacao.
- Exibir mensagens de erro por campo.
- Validar nome unico no backend.
- Validar intervalo de datas.
- Validar fases dentro do periodo.
- Validar fases sem sobreposicao.
- Validar nome unico de fase por histograma.
- Validar nome unico de coluna customizavel por histograma.
- Validar cores das secoes em formato hexadecimal.

## 5. Tela do histograma

### 5.1 Estrutura visual geral

A tela deve exibir:

1. Titulo do histograma.
2. Subtitulo/descricao.
3. Tabela do histograma.

A tabela deve ser dividida conceitualmente em:

- Parte esquerda: recursos e atributos.
- Parte direita: quantitativos diarios.

### 5.2 Header temporal da parte direita

A parte direita da tabela deve possuir cabecalho com as seguintes linhas:

1. Dias corridos desde o inicio do histograma.
2. Dias uteis decorridos desde o inicio do histograma.
3. Nome das fases, usando agrupamento visual sobre as colunas de dias pertencentes a fase.
4. Contagem numerica do dia dentro da fase, reiniciando em 1 no inicio de cada fase.
5. Nome do mes e ano no formato `mmm/yy`, por exemplo `jan/26`, com agrupamento por mes.
6. Dia da semana abreviado com 3 caracteres, por exemplo `seg`, `ter`, `qua`.
7. Dia do mes no formato `dd`, por exemplo `01`, `02`, `31`.

Regras:

- O calculo de dias corridos considera todos os dias desde o inicio.
- O calculo de dias uteis deve considerar dias de segunda a sexta inicialmente.
- Fins de semana devem ter fundo levemente diferente.
- O `stepDays` do histograma define quais dias aparecem como colunas.
- Se `stepDays = 1`, todos os dias aparecem.
- Se `stepDays = 7`, exibir uma coluna a cada 7 dias, respeitando o periodo.
- Mesmo com step, os calculos devem permanecer coerentes com o periodo real.

### 5.3 Header da parte esquerda

A parte esquerda deve possuir:

- Primeira linha fixa com o titulo `RECURSOS`.
- Coluna fixa obrigatoria `Nome do recurso`.
- Colunas customizaveis definidas pelo usuario.
- Acoes para adicionar/remover colunas customizaveis.

Regras:

- `Nome do recurso` nao pode ser removido.
- Colunas customizaveis podem ser do tipo `string`, `dropdown` ou `tags`.
- Colunas customizaveis podem ser adicionadas ou removidas pelo usuario.

### 5.4 Secoes e recursos

Comportamento esperado:

- Recursos so podem existir dentro de uma secao.
- O header de cada secao deve exibir o nome da secao.
- O header de cada secao deve usar a cor customizada pelo usuario.
- Cada secao deve ter uma cor de fundo diferente quando o usuario assim configurar.
- O usuario pode editar a cor da secao.
- O botao `+` no header da secao adiciona um novo recurso dentro daquela secao.
- Caso nao exista nenhuma secao, o fluxo de adicionar recurso deve abrir primeiro o cadastro de secao.
- Recursos devem ser ordenaveis dentro da secao, se possivel.
- Secoes devem ser ordenaveis, se possivel.

### 5.5 Totais

Implementar:

- Linha de total parcial para cada secao.
- Linha de total geral do histograma.

Regras:

- A linha de total parcial da secao deve ficar logo apos os recursos daquela secao.
- Para cada dia, o total parcial deve somar os quantitativos dos recursos daquela secao.
- A linha de total geral deve ficar ao final da tabela.
- Para cada dia, o total geral deve somar os totais parciais das secoes.
- Totais devem atualizar automaticamente quando um quantitativo for alterado.

## 6. UX e interacoes

- Usar componentes simples, claros e responsivos.
- Usar Tailwind para estados visuais de foco, hover, erro e desabilitado.
- Usar modais, drawers ou paineis laterais para formularios se fizer sentido.
- Evitar recarregar a pagina para acoes CRUD.
- Exibir estados de carregamento.
- Exibir mensagens de sucesso/erro.
- Confirmar a remocao de entidades destrutivas, como fases, secoes, recursos e colunas customizadas.
- Se uma coluna customizada for removida, definir estrategia clara para excluir tambem seus valores associados.
- Se uma secao for removida, avisar que seus recursos e quantitativos serao afetados.

## 7. API sugerida

Endpoints sugeridos:

- `GET /api/histograms`
- `POST /api/histograms`
- `GET /api/histograms/:id`
- `PUT /api/histograms/:id`
- `DELETE /api/histograms/:id`
- `POST /api/histograms/:id/phases`
- `PUT /api/phases/:id`
- `DELETE /api/phases/:id`
- `POST /api/histograms/:id/sections`
- `PUT /api/sections/:id`
- `DELETE /api/sections/:id`
- `POST /api/sections/:id/resources`
- `PUT /api/resources/:id`
- `DELETE /api/resources/:id`
- `POST /api/histograms/:id/custom-columns`
- `PUT /api/custom-columns/:id`
- `DELETE /api/custom-columns/:id`
- `PUT /api/resources/:id/custom-values`
- `PUT /api/resources/:id/quantities`
- `GET /api/histograms/:id/table-data`

O endpoint `table-data` deve retornar os dados ja estruturados para renderizacao eficiente da tabela:

- Metadados do histograma.
- Lista de dias exibidos conforme step.
- Linhas de cabecalho temporal.
- Fases associadas aos dias.
- Secoes com cor customizada.
- Recursos por secao.
- Colunas customizaveis.
- Quantitativos por recurso/dia.
- Totais parciais por secao.
- Total geral por dia.

## 8. Modelo SQLAlchemy sugerido

Crie modelos SQLAlchemy compativeis com SQL Server contendo, no minimo:

- `Histogram`
- `ProjectPhase`
- `ResourceSection`
- `ResourceCustomColumn`
- `Resource`
- `ResourceCustomValue`
- `ResourceQuantity`

Constraints importantes:

- `Histogram.name` unico.
- `ProjectPhase`: unique composto por `histogramId` + `name`.
- `ResourceSection`: unique composto por `histogramId` + `name`.
- `ResourceCustomColumn`: unique composto por `histogramId` + `name`.
- `ResourceQuantity`: unique composto por `resourceId` + `date`.
- Relacionamentos com cascade ou restricoes explicitas bem definidas.

Observacao: a regra de fases nao sobrepostas provavelmente precisara ser validada na camada de aplicacao, pois nao e trivial expressar como constraint simples em SQL Server via SQLAlchemy.

## 9. Calculos esperados

### 9.1 Dias exibidos

Gerar lista de datas entre `startDate` e `endDate`, respeitando `stepDays`.

### 9.2 Dias corridos

Para cada data exibida:

- `diasCorridos = diferencaEmDias(data, startDate) + 1`

### 9.3 Dias uteis decorridos

Para cada data exibida:

- Contar dias de segunda a sexta entre `startDate` e a data exibida.
- Inicialmente nao considerar feriados, mas estruturar o codigo para permitir evolucao futura.

### 9.4 Fases

Para cada data exibida:

- Identificar a fase cujo intervalo contem a data.
- Exibir o nome da fase agrupado visualmente.
- Exibir o numero do dia dentro da fase, reiniciando a contagem em 1 no inicio da fase.

### 9.5 Totais

Para cada secao e data:

- `totalParcialSecao[data] = soma(quantity dos recursos da secao naquela data)`

Para o total geral:

- `totalGeral[data] = soma(totalParcialSecao[data] de todas as secoes)`

## 10. Entregaveis esperados

Entregar:

- Projeto React + Vite + TypeScript.
- Tailwind configurado.
- Formularios com react-hook-form uncontrolled.
- Schemas Zod para validacao.
- Backend Python/FastAPI com API HTTP.
- SQLAlchemy configurado para SQL Server.
- Docker Compose para SQL Server em desenvolvimento.
- `.env.example` com variaveis do banco e da aplicacao.
- Migrations Alembic.
- Tela de listagem de histogramas.
- Tela/formulario de criacao e edicao de histograma.
- CRUD de fases.
- CRUD de secoes com cor customizavel.
- CRUD de colunas customizaveis.
- CRUD de recursos por secao.
- Edicao de quantitativos diarios.
- Tabela de histograma com headers fixos, rolagem e linhas virtualizadas.
- Total parcial por secao.
- Total geral por dia.
- Destaque visual para fins de semana.
- Testes unitarios para validacoes e calculos principais, especialmente:
  - periodo do histograma;
  - fase fora do periodo;
  - fase sobreposta;
  - nomes unicos por escopo;
  - geracao de dias por step;
  - dias corridos;
  - dias uteis;
  - contagem de dias da fase;
  - totais parciais por secao;
  - total geral.

## 11. Criterios de aceite

- Deve ser possivel cadastrar um histograma com nome unico, descricao, datas e step.
- Deve ser possivel cadastrar fases validas dentro do periodo do histograma.
- O sistema deve impedir fases sobrepostas.
- Deve ser possivel cadastrar secoes com nome e cor customizada.
- O header de cada secao deve usar a cor customizada pelo usuario.
- Deve ser possivel cadastrar recursos dentro das secoes.
- Deve ser possivel cadastrar colunas customizaveis de tipos string, dropdown e tags.
- Deve ser possivel informar quantitativos por recurso/dia.
- A tabela deve exibir dias corridos, dias uteis, fases, dia da fase, mes/ano, dia da semana e dia do mes.
- Fins de semana devem ser visualmente diferenciados.
- Cada secao deve possuir linha de total parcial.
- O histograma deve possuir linha de total geral.
- A tabela deve ter rolagem com headers fixos.
- As linhas devem ser virtualizadas.
- O projeto deve executar em ambiente local usando SQL Server dockerizado.
- O acesso ao banco deve usar SQLAlchemy ORM.
- As credenciais devem vir de variaveis de ambiente.
```

