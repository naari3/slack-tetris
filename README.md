# Tetris for Slack

チャットボットハッカソンのサンプルです．
Slackでテトリスを遊ぶことができます．

# Get start

1. https://my.slack.com/apps/new/A0F7YS25R-bots で新しくBotを作成する
2. imgフォルダにあるpngファイルをすべてファイル名をemoji名としてslackに登録する
3. Botを取得する

```sh
$ git clone https://github.com/naari3/slack-tetris.git
$ cd slack-tetris
```

4. 取得したslack-tetrisディレクトリのmanifest.ymlに環境変数を追加する

```yaml
---
  ...
  env:
    SLACK_API_TOKEN: <1.のAPI Token>
    BOT_NAME: <Bot名>
```

5. Cloud FoundryにBotをPushする

```sh
$ cf login -a URL -u USER -p PASS
$ cf push <アプリ名>
```

6. テトリスで遊ぶ

# Commands

Slackで以下の用に投稿するとBotを操作できます．

bot名 command

入力可能なコマンドは以下の通りです．
未定義のコマンドを入力するとヘルプが表示されます．

```skack
start: テトリスを開始
down|d: ブロックを1マス下に移動
harddrop|h: ブロックを一番したまで移動
left|l: ブロックを1マス左に移動
right|r: ブロックを1マス右に移動
turn|t: プロックを回転
stop: テトリスを終了
```

## Command repeating

次のように入力することでコマンドの連続実行が可能になります

bot名 command 4 command2 2 command3

例: bot名 left 4 turn 2 harddrop

# Reference

* https://api.slack.com/apps
* http://euphorie.sakura.ne.jp/junk/page_python_teto.html
* http://slackapi.github.io/python-slackclient/index.html
* https://github.com/slackapi/python-slack-events-api
* https://www.cloudfoundry.org/
* https://www.flaticon.com/
