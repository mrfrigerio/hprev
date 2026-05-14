# Instrucoes completas para o agente desenvolver o sistema HPRev

Use este arquivo como instrucao completa para solicitar a um agente o desenvolvimento do sistema HPRev/HPrev.

## 1. Contexto e objetivo

Desenvolver um sistema web chamado HPRev/HPrev para cadastro, manutencao e visualizacao de histogramas de mao de obra e equipamentos.

O sistema deve permitir que o usuario:

- Cadastre histogramas.
- Cadastre fases do projeto dentro de cada histograma.
- Cadastre secoes de recursos dentro de cada histograma.
- Cadastre recursos dentro de cada secao.
- Cadastre colunas customizaveis para os recursos.
- Informe quantitativos diarios para cada recurso.
- Visualize o histograma como uma tabela com cabecalho temporal, recursos, secoes, total parcial por secao e total geral por dia.

Existe uma planilha de referencia visual no repositorio:

- `docs/hprev_histograma_esboco_visual.xlsx`

Use essa planilha como guia visual para a tela principal do histograma.

## 2. Stack obrigatoria

### 2.1 Frontend

- ReactJS.
- Vite.
- TypeScript.
- Tailwind CSS.
- react-hook-form para formularios.
- Formularios preferencialmente uncontrolled, usando `register`, `defaultValues` e os recursos nativos do react-hook-form.
- Zod para validacao.
- Integracao Zod + react-hook-form por meio de resolver apropriado.

### 2.2 Tabela do histograma

- A tabela deve ser rolavel.
- Os headers devem permanecer fixos durante a rolagem.
- As colunas fixas da esquerda, onde ficam recurso e atributos, devem permanecer visiveis ou pelo menos alinhadas com o corpo da tabela.
- As linhas da tabela devem ser virtualizadas para evitar lentidao com muitos recursos.
- Usar TanStack Virtual ou biblioteca equivalente para virtualizacao de linhas.
- A rolagem horizontal deve permitir navegar pelos dias do histograma.
- O design deve suportar histogramas com muitos dias e muitos recursos.

### 2.3 Backend e banco

- Utilizar Prisma ORM.
- Utilizar Microsoft SQL Server como banco inicial.
- Em desenvolvimento, o SQL Server deve ser dockerizado.
- Criar configuracao Docker Compose para ambiente local.
- Criar `.env.example` com as variaveis necessarias.
- Nao versionar segredos reais.
- Nao hardcodar credenciais no codigo.

Variaveis esperadas no ambiente:

```env
DATABASE_URL="sqlserver://localhost:1433;database=hprev;user=sa;password=YourStrong!Passw0rd;trustServerCertificate=true"
SQLSERVER_HOST=localhost
SQLSERVER_PORT=1433
SQLSERVER_DATABASE=hprev
SQLSERVER_USER=sa
SQLSERVER_PASSWORD=YourStrong!Passw0rd
SQLSERVER_SA_PASSWORD=YourStrong!Passw0rd
APP_PORT=3000
VITE_API_BASE_URL=http://localhost:3000/api
```

### 2.4 Arquitetura sugerida

Como o Prisma deve rodar no backend, implementar:

- Frontend React/Vite/TypeScript.
- Backend Node.js/TypeScript com API HTTP.
- Prisma Client no backend.
- SQL Server via Docker Compose em desenvolvimento.
- Scripts para rodar frontend, backend, migrations e banco local.

Pode usar Express, Fastify ou framework HTTP equivalente. Escolha uma opcao simples e consistente.

## 3. Requisitos funcionais

### 3.1 Cadastro de histograma

O sistema deve permitir cadastrar e editar histogramas com:

- Nome do histograma.
- Descricao do histograma.
- Data de inicio.
- Data de termino.
- Step em dias.

Regras:

- Nome e obrigatorio.
- Nome deve ser unico no sistema.
- Nome sera usado como titulo do histograma.
- Descricao sera usada como subtitulo.
- Data de inicio e obrigatoria.
- Data de termino e obrigatoria.
- Data de termino deve ser maior ou igual a data de inicio.
- Step em dias e obrigatorio.
- Step deve ser inteiro positivo.
- Step controla de quantos em quantos dias as colunas serao exibidas na tabela do histograma.

### 3.2 Fases do projeto

Dentro do formulario do histograma, o usuario deve poder cadastrar fases do projeto.

Campos da fase:

- Nome da fase.
- Data de inicio.
- Data de termino.
- Ordem de exibicao, quando necessario.

Regras:

- Uma fase pertence a um histograma.
- Nome da fase e obrigatorio.
- Nome da fase deve ser unico dentro do escopo do histograma.
- Data de inicio e data de termino da fase devem estar dentro do periodo do histograma.
- Data de termino da fase deve ser maior ou igual a data de inicio da fase.
- Fases de um mesmo histograma nao podem se sobrepor.
- Validar sobreposicao no backend antes de persistir.
- Exibir mensagem clara quando o usuario tentar criar fase invalida.

### 3.3 Secoes de recursos

O sistema deve permitir cadastrar secoes dentro de cada histograma.

Campos da secao:

- Nome da secao.
- Cor do header da secao.
- Ordem de exibicao.

Regras:

- Uma secao pertence a um histograma.
- Nome da secao e obrigatorio.
- Recomenda-se nome unico dentro do histograma.
- A cor deve ser customizavel pelo usuario.
- A cor deve ser armazenada em formato hexadecimal, por exemplo `#0F766E`.
- Cada header de secao deve usar a cor cadastrada pelo usuario.
- Cada secao deve poder ter cor diferente.
- Deve existir uma linha de total parcial para cada secao.
- A linha de total parcial deve aparecer logo apos os recursos daquela secao.

### 3.4 Recursos

O sistema deve permitir cadastrar recursos dentro de secoes.

Campos fixos do recurso:

- Nome do recurso.
- Secao.
- Ordem.

Regras:

- Todo recurso pertence a uma secao.
- Todo recurso tambem pertence ao histograma da secao.
- Nome do recurso e obrigatorio.
- A coluna "Nome do recurso" e fixa, obrigatoria e nao pode ser removida.
- Recursos so podem ser cadastrados dentro de uma secao.
- Se nao houver nenhuma secao cadastrada, o botao de adicionar recurso deve abrir primeiro o cadastro de secao.
- Se ja houver secoes, cada header de secao deve exibir um botao `+` para adicionar recurso naquela secao.

### 3.5 Colunas customizaveis dos recursos

Alem da coluna fixa "Nome do recurso", o usuario deve poder adicionar colunas customizaveis.

Campos da coluna customizavel:

- Nome da coluna.
- Tipo.
- Obrigatoria ou nao.
- Opcoes, quando aplicavel.
- Ordem.

Tipos permitidos:

- `string`: texto ou numero livre armazenado como texto.
- `dropdown`: selecao de um valor entre opcoes pre-definidas pelo usuario.
- `tags`: multiplos valores/tags.

Regras:

- Colunas customizaveis pertencem ao histograma.
- Nome da coluna customizavel e obrigatorio.
- Nome da coluna customizavel deve ser unico dentro do histograma.
- Usuario pode adicionar colunas customizaveis.
- Usuario pode remover colunas customizaveis.
- Ao remover coluna customizavel, definir comportamento para remover tambem os valores associados.
- A coluna fixa "Nome do recurso" nao pode ser renomeada, removida ou convertida em coluna customizavel.

### 3.6 Valores customizados dos recursos

Cada recurso deve poder armazenar valores para as colunas customizaveis.

Regras:

- Para coluna `string`, aceitar texto livre.
- Para coluna `dropdown`, aceitar apenas valores cadastrados como opcoes.
- Para coluna `tags`, aceitar multiplas tags.
- Validar os valores no backend.

### 3.7 Quantitativos diarios

Cada recurso deve possuir quantitativos por dia do histograma.

Campos:

- Recurso.
- Data.
- Quantidade.

Regras:

- Data deve estar dentro do periodo do histograma.
- Quantidade deve ser numerica.
- Quantidade nao pode ser negativa.
- Permitir decimal, salvo se houver regra futura exigindo inteiro.
- Deve existir no maximo um quantitativo por recurso e data.
- Usuario deve conseguir editar quantitativos diretamente ou por formulario rapido na tabela.
- Fins de semana devem ter cor de fundo levemente diferente.

### 3.8 Totais

Implementar totais no histograma:

- Total parcial por secao.
- Total geral por dia.

Regras:

- Cada secao deve ter uma linha de total parcial.
- O total parcial da secao em cada dia deve somar os quantitativos dos recursos daquela secao naquele dia.
- A linha de total geral deve ficar ao final da tabela.
- O total geral de cada dia deve somar os totais parciais das secoes.
- Totais devem atualizar quando o usuario alterar quantitativos.

## 4. Estrutura visual da tela do histograma

### 4.1 Titulo e subtitulo

No topo da tela:

- Exibir o nome do histograma como titulo.
- Exibir a descricao como subtitulo.

### 4.2 Parte esquerda da tabela

A parte esquerda representa recursos e atributos.

Deve conter:

- Header fixo com o texto `RECURSOS`.
- Coluna fixa `Nome do recurso`.
- Colunas customizaveis definidas pelo usuario.
- Headers de secao com cor customizada pelo usuario.
- Botao `+` no header da secao para adicionar recurso.
- Linha de total parcial por secao.

### 4.3 Parte direita da tabela

A parte direita contem os quantitativos diarios.

O header temporal deve ter as seguintes linhas:

1. Dias corridos desde o inicio do histograma.
2. Dias uteis decorridos desde o inicio do histograma.
3. Nome das fases.
4. Contagem numerica de dias dentro de cada fase, reiniciando em 1 a cada nova fase.
5. Nome do mes e ano no formato `mmm/yy`, por exemplo `jan/26`.
6. Dia da semana abreviado com 3 caracteres, por exemplo `seg`, `ter`, `qua`.
7. Dia do mes no formato `dd`, por exemplo `01`, `02`, `31`.

Regras:

- Dias corridos contam todos os dias desde o inicio do histograma.
- Dias uteis contam inicialmente segunda a sexta.
- Feriados nao precisam ser considerados na primeira versao, mas o codigo deve permitir evolucao futura.
- O nome da fase deve aparecer agrupado visualmente sobre os dias daquela fase.
- O mes deve aparecer agrupado visualmente sobre os dias daquele mes.
- Fins de semana devem ter cor de fundo levemente diferente.
- Step controla quais datas aparecem como colunas.

## 5. Calculos

### 5.1 Datas exibidas

Gerar datas entre `startDate` e `endDate`, respeitando `stepDays`.

Exemplo:

- `stepDays = 1`: exibir todos os dias.
- `stepDays = 7`: exibir uma data a cada 7 dias.

### 5.2 Dias corridos

Formula:

```text
diasCorridos = diferencaEmDias(dataExibida, dataInicioHistograma) + 1
```

### 5.3 Dias uteis

Contar dias de segunda a sexta entre o inicio do histograma e a data exibida.

### 5.4 Dia da fase

Para cada data exibida:

- Identificar a fase que contem a data.
- Calcular a diferenca entre a data exibida e o inicio da fase.
- Reiniciar a contagem em 1 no inicio de cada fase.

### 5.5 Total parcial por secao

Formula:

```text
totalParcialSecao[data] = soma(quantidade dos recursos da secao naquela data)
```

### 5.6 Total geral

Formula:

```text
totalGeral[data] = soma(totalParcialSecao[data] de todas as secoes)
```

## 6. Modelo de dados sugerido

Criar schema Prisma para SQL Server com, no minimo, os modelos abaixo.

### 6.1 Histogram

Campos sugeridos:

- `id`
- `name`
- `description`
- `startDate`
- `endDate`
- `stepDays`
- `createdAt`
- `updatedAt`

Constraints:

- `name` unico.

### 6.2 ProjectPhase

Campos sugeridos:

- `id`
- `histogramId`
- `name`
- `startDate`
- `endDate`
- `order`
- `createdAt`
- `updatedAt`

Constraints:

- Unique composto por `histogramId` + `name`.

### 6.3 ResourceSection

Campos sugeridos:

- `id`
- `histogramId`
- `name`
- `colorHex`
- `order`
- `createdAt`
- `updatedAt`

Constraints:

- Unique composto por `histogramId` + `name`.

### 6.4 ResourceCustomColumn

Campos sugeridos:

- `id`
- `histogramId`
- `name`
- `type`
- `required`
- `options`
- `order`
- `createdAt`
- `updatedAt`

Constraints:

- Unique composto por `histogramId` + `name`.

Observacao:

- `options` pode ser JSON/string serializada ou uma tabela relacional separada, conforme melhor compatibilidade com Prisma e SQL Server.

### 6.5 Resource

Campos sugeridos:

- `id`
- `histogramId`
- `sectionId`
- `name`
- `order`
- `createdAt`
- `updatedAt`

### 6.6 ResourceCustomValue

Campos sugeridos:

- `id`
- `resourceId`
- `customColumnId`
- `value`

Constraints:

- Unique composto por `resourceId` + `customColumnId`.

### 6.7 ResourceQuantity

Campos sugeridos:

- `id`
- `resourceId`
- `date`
- `quantity`
- `createdAt`
- `updatedAt`

Constraints:

- Unique composto por `resourceId` + `date`.

## 7. API sugerida

Implementar endpoints equivalentes aos abaixo:

### 7.1 Histogramas

- `GET /api/histograms`
- `POST /api/histograms`
- `GET /api/histograms/:id`
- `PUT /api/histograms/:id`
- `DELETE /api/histograms/:id`

### 7.2 Fases

- `POST /api/histograms/:id/phases`
- `PUT /api/phases/:id`
- `DELETE /api/phases/:id`

### 7.3 Secoes

- `POST /api/histograms/:id/sections`
- `PUT /api/sections/:id`
- `DELETE /api/sections/:id`

### 7.4 Recursos

- `POST /api/sections/:id/resources`
- `PUT /api/resources/:id`
- `DELETE /api/resources/:id`

### 7.5 Colunas customizaveis

- `POST /api/histograms/:id/custom-columns`
- `PUT /api/custom-columns/:id`
- `DELETE /api/custom-columns/:id`

### 7.6 Valores e quantitativos

- `PUT /api/resources/:id/custom-values`
- `PUT /api/resources/:id/quantities`

### 7.7 Dados da tabela

- `GET /api/histograms/:id/table-data`

O endpoint `table-data` deve retornar dados prontos para renderizacao eficiente:

- Metadados do histograma.
- Datas exibidas conforme step.
- Linhas do cabecalho temporal.
- Fases associadas aos dias.
- Meses agrupados.
- Secoes com nome, ordem e cor customizada.
- Recursos por secao.
- Colunas customizaveis.
- Valores customizados dos recursos.
- Quantitativos por recurso e data.
- Totais parciais por secao.
- Total geral por data.

## 8. Validacoes

### 8.1 Validacoes com Zod no frontend

Criar schemas Zod para:

- Histograma.
- Fase.
- Secao.
- Coluna customizavel.
- Recurso.
- Valores customizados.
- Quantitativos.

### 8.2 Validacoes obrigatorias no backend

Mesmo com validacao no frontend, repetir validacoes criticas no backend:

- Nome unico do histograma.
- Periodo valido do histograma.
- Step positivo.
- Nome unico da fase dentro do histograma.
- Fase dentro do periodo do histograma.
- Fases sem sobreposicao.
- Nome unico da secao dentro do histograma.
- Cor hexadecimal valida para secao.
- Nome unico da coluna customizavel dentro do histograma.
- Tipo valido de coluna customizavel.
- Dropdown com opcoes validas.
- Recurso dentro de secao existente.
- Quantitativo dentro do periodo do histograma.
- Quantitativo nao negativo.
- Apenas um quantitativo por recurso/data.

## 9. UX esperada

- Interface clara e responsiva.
- Usar Tailwind para layout, espacamento, cores e estados.
- Mostrar loading states.
- Mostrar empty states.
- Mostrar mensagens de erro e sucesso.
- Confirmar acoes destrutivas.
- Evitar reload da pagina para operacoes CRUD.
- Permitir edicao fluida dos quantitativos.
- Manter alinhamento entre cabecalho e corpo da tabela.
- Destacar visualmente fins de semana.
- Destacar visualmente headers de secao usando a cor configurada pelo usuario.
- Garantir contraste minimo entre texto e cor de fundo da secao. Se necessario, ajustar automaticamente a cor do texto entre claro/escuro.

## 10. Requisitos de performance

- Virtualizar linhas da tabela.
- Evitar renderizar todos os recursos quando houver muitas linhas.
- Evitar recalculos desnecessarios de datas e totais.
- Memoizar estruturas derivadas quando fizer sentido.
- Buscar do backend apenas os dados necessarios para a tela.
- Estruturar o endpoint de dados da tabela para reduzir processamento repetido no frontend.

## 11. Docker e ambiente local

Entregar:

- `docker-compose.yml` com SQL Server.
- `.env.example` com variaveis documentadas.
- Scripts no `package.json` para:
  - instalar dependencias;
  - subir ambiente dev;
  - executar migrations;
  - gerar Prisma Client;
  - rodar frontend;
  - rodar backend;
  - rodar testes.

Exemplo de servico SQL Server no Docker Compose:

```yaml
services:
  sqlserver:
    image: mcr.microsoft.com/mssql/server:2022-latest
    environment:
      ACCEPT_EULA: "Y"
      MSSQL_SA_PASSWORD: "${SQLSERVER_SA_PASSWORD}"
    ports:
      - "${SQLSERVER_PORT:-1433}:1433"
    volumes:
      - sqlserver-data:/var/opt/mssql

volumes:
  sqlserver-data:
```

## 12. Testes esperados

Criar testes para regras principais:

- Cadastro de histograma com periodo valido.
- Rejeicao de histograma com data final menor que data inicial.
- Rejeicao de step invalido.
- Rejeicao de fase fora do periodo do histograma.
- Rejeicao de fase sobreposta.
- Nome unico de fase por histograma.
- Nome unico de secao por histograma.
- Validacao de cor hexadecimal de secao.
- Nome unico de coluna customizavel por histograma.
- Geracao de datas conforme step.
- Calculo de dias corridos.
- Calculo de dias uteis.
- Calculo de dia da fase.
- Calculo de total parcial por secao.
- Calculo de total geral.

## 13. Entregaveis

O agente deve entregar:

- Projeto frontend React + Vite + TypeScript.
- Tailwind configurado.
- Formularios com react-hook-form uncontrolled.
- Schemas Zod.
- Backend Node.js/TypeScript.
- API HTTP.
- Prisma configurado para SQL Server.
- Migrations Prisma.
- Docker Compose com SQL Server.
- `.env.example`.
- Tela de listagem de histogramas.
- Tela de cadastro/edicao de histograma.
- CRUD de fases.
- CRUD de secoes com cor customizavel.
- CRUD de colunas customizaveis.
- CRUD de recursos por secao.
- Edicao de valores customizados dos recursos.
- Edicao de quantitativos diarios.
- Tela de histograma com headers fixos, rolagem e linhas virtualizadas.
- Total parcial por secao.
- Total geral por dia.
- Destaque visual de fins de semana.
- Testes para validacoes e calculos principais.
- Documentacao breve no README explicando como rodar localmente.

## 14. Criterios de aceite

O trabalho sera considerado completo quando:

- For possivel rodar o ambiente local com SQL Server dockerizado.
- O Prisma estiver conectado ao SQL Server usando variaveis de ambiente.
- For possivel criar, listar, editar e remover histogramas.
- O nome do histograma for validado como unico.
- For possivel criar fases dentro do periodo do histograma.
- O sistema impedir fases sobrepostas.
- For possivel criar secoes com cor customizavel.
- O header da secao usar a cor cadastrada pelo usuario.
- For possivel criar recursos dentro de secoes.
- For possivel criar colunas customizaveis de tipos `string`, `dropdown` e `tags`.
- For possivel preencher valores customizados dos recursos.
- For possivel preencher quantitativos diarios por recurso.
- A tabela exibir cabecalho temporal completo.
- A tabela diferenciar fins de semana visualmente.
- A tabela exibir total parcial por secao.
- A tabela exibir total geral por dia.
- A tabela manter headers fixos durante rolagem.
- As linhas da tabela forem virtualizadas.
- Os formularios usarem react-hook-form com abordagem uncontrolled.
- As validacoes usarem Zod.
- A documentacao de execucao estiver clara.

