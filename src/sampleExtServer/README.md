# SampleExtServer

サンプルの外部補助出力サーバ．
受信したデータをおうむ返しに返答しているだけです．

```sh
python main.py --port 8888
```

にて起動します． 

D4ACの外部サーバ設定に，

`http://{ipアドレス}:8888/dummyResponse/`

を設定してください．おうむ返しなので，何も変化がなくてOKです．

