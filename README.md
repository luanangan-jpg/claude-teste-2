# Agregador de Notícias Internacionais e Brasileiras

Este é um projeto completo e autônomo para curadoria e agregação de notícias. 

## Como publicar e hospedar de graça

Para que o site fique disponível na internet e atualizando sozinho, siga estes passos exatos no seu GitHub:

### Passo 1: Criar o Repositório no GitHub
1. Acesse [github.com](https://github.com/) e faça login.
2. No canto superior direito, clique no botão **+** e selecione **New repository**.
3. Em "Repository name", digite `agregador-noticias`.
4. Deixe a opção **Public** marcada (é necessário para hospedar gratuitamente o site de forma fácil).
5. Clique em **Create repository**.

### Passo 2: Enviar os arquivos para o GitHub
Você pode enviar os arquivos arrastando-os pelo site ou usando o Git pelo terminal.
Se quiser usar a opção de arrastar pelo site:
1. Na página do seu novo repositório no GitHub, clique no link azul **"uploading an existing file"**.
2. Selecione e arraste **todos** os arquivos que o Antigravity gerou para você (incluindo as pastas `.github`, e os arquivos `.html`, `.css`, `.js`, `.py`, `.json`).
3. Clique em **Commit changes**.

### Passo 3: Ativar o Site Público (GitHub Pages)
1. No seu repositório do GitHub, clique na aba **Settings** (Configurações).
2. No menu lateral esquerdo, clique em **Pages**.
3. Em "Build and deployment", na seção **Source**, selecione "Deploy from a branch".
4. Logo abaixo, onde diz "Branch", clique no botão que diz `None`, selecione `main` (ou `master`), e clique em **Save**.
5. Aguarde cerca de 1 a 2 minutos. Recarregue a página e um link aparecerá na parte superior (ex: `https://seu-usuario.github.io/agregador-noticias/`). Este é o link permanente do seu site!

### Passo 4: Como as atualizações funcionam
O sistema já está configurado (via GitHub Actions) para rodar o arquivo `scraper.py` 3 vezes ao dia. 
Esse arquivo baixa as últimas notícias do `sources.json`, categoriza, e recria o `news.json`. 
A cada nova coleta, o robô do GitHub automaticamente salva (faz um commit) no repositório, e o seu site já exibe as novidades. Você não precisa fazer nada!

### Passo 5: Como adicionar novas fontes
Se quiser adicionar um novo jornal no futuro:
1. Vá até o seu repositório no GitHub.
2. Clique no arquivo `sources.json` e depois no ícone de "Lápis" (Editar).
3. Adicione um novo bloco com o formato exigido: `"name"`, `"url"` (deve ser um link RSS) e `"reliability"`.
4. Clique em **Commit changes**. O robô fará o resto!
