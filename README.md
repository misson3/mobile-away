# mobile-away

Mar05, 2022, ms

うちの実験的Web記事：Mobile-Away: ケータイお預けステーションで使っているコードたちです。



Nov12, 2022, ms

Simpler version

- toggl trackへの記録のみ
- 積算時間、ポイント、ボーナス点などすべて廃止。これによりRaspberry pi上のdbとのやり取りが不要になった。
- 22時から朝6時までなどの時間帯モードを廃止。
- adafruit ioからの時間取得を削除。toggl trackからのresponseに含まれる情報からstart, stopのtimestampを作成するようにした。UTCをlocal時間にするところで少々てこずった。
