# hbstudy #41 IDCF-Cloud を 自作auto-scaling

[hbstudy#41 x IDCFクラウドハンズオン](http://connpass.com/event/1658/)で
snicker_jpが使った、ファイルたちです。

## Contents
* bin
 - scale.sh  
 Redisに見に行って、一定間隔でScaleするSHELL
 - scale2.sh  
 Redisに見に行って、一定間隔でScaleするSHELL その2
* fabfile.py (main fabric resource)  
fabric のリソースファイルで色々書いてあるメインです
* hello_py.cgi  
ホスト名を表示する、cgiです
* loadavg.rc    
monitの、LoadAverage 監視設定

## Other resource
### PDF Source
[Hbstudy41 auto scaling](http://www.slideshare.net/tafujish/hbstudy41-auto-scalingv13) from Fujishiro Takuya

### Event Pages
[hbstudy#41 x IDCFクラウドハンズオン](http://connpass.com/event/1658/) at connpass