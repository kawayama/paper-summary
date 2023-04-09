# 論文要約＆配信ツール
## 概要
- [最新の論文をChatGPTで要約して毎朝Slackに共有してくれるbotを作る！](https://zenn.dev/ozushi/articles/ebe3f47bf50a86) をいい感じに実装したもの
- Docker環境の構築、エラー処理、複数のクエリなどに追加で対応しています
- 自分で使っているので、気が向いたら更新します

## 使い方
1. PCにdockerをインストールする
   - クラウド上の仮想マシンやVPSなどの常時起動しているものが良いです
   - リクエストしか飛ばさないので、ポートを開けておく必要はありません
2. このフォルダのディレクトリに移動
3. config.iniに以下を入力
   - `openai.api_key`: OpenAIのAPIキー (`sk-xxxxxxxxxxxxxxxxx...`)
   - `slack.webhook_url`: SlackのWebhook URL (`https://hooks.slack.com/services/XXXX.../XXXX.../XXXX...`)
4. data/query_list.txtに1行ずつクエリを書いておく
   - [arXiv API User's Manual - arXiv info](https://info.arxiv.org/help/api/user-manual.html#query_details)
   - 初期状態だとテスト用のクエリが入力されています
5. `docker compose up -d` で実行
6. 毎日7時に論文がクエリごとに3本slackに届く
   - たとえばクエリ2個だったら1日6本の論文が届く
   - 適当に `paper` チャンネルに届くようにしているので、作成しておいて下さい


## 今後
- [ ] DockerHubから直接pullできるようにする
- [ ] 論文の取得先を増やす
- [ ] 1日の取得量や配信先を簡単に設定できるようにする
