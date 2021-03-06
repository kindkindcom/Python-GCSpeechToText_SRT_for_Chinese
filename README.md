# Python-GCSpeechToText_SRT_for_Chinese
谷歌云声音转文字之SRT字幕中文语言版 | Google Cloud SpeechToText, SRT for Chinese
## SRT_for_Chinese 2.0
**Author:kindkind.com**

*脚本编写于 python 3.7*

#### 说明：
```
谷歌云服务及SRT转换脚本均参考了该项目：
https://github.com/darshan-majithiya/Generate-SRT-File-using-Google-Cloud-s-Speech-to-Text-API.git

使用过程中发现，对于上面项目中仅仅按照时间段分割英语单词的方式，非常不适合中国人以字为单位的语言习惯，
经过反复测试修改，始终有语句中断错乱、时码偏差较大的问题，
最后干脆将分割方式按照我的预想进行了重写，并添加了自动判断发音习惯参考值的功能（比较简陋，但是可以自适应不同人的语速了），
现在的版本是我正在使用，感觉比较良好的一个版本，现只分享出转换SRT字幕部分的代码，
完整的谷歌云语音识别服务的上传、接收脚本，请参考上面的项目。
```

#### 已知问题：
```
1.谷歌声音识别服务转换出来的内容，会分为几个段落，但鉴于转换之后的一些缺陷（个人感觉是谷歌开发人员不怎么用这个服务吧）
  对于每段最后一个字的时码无法与下一段落的起始字时间对接，导致每个段落最后一句显示的时长不够。
  现将毫秒数x2以便不至于过短，我也懒得继续尝试，反正还需要用字幕软件校对一遍内容及部分时码。
  
2.语音识别服务产生的时码，跟音频时码有偏差，基本上整体会慢不到1秒（也有部分句子时码刚好），
  使用SRT字幕编辑软件进行整体提前修正即可。
  
3.因为没有使用单词模型进行对照断句（感觉个人使用，弄个模型库不太现实），有些字说的快的时候会出现超长的句子，
  而有些字又会超短，当然也跟语音识别服务的时码缺陷有关，暂时无法解决，只有字幕软件校对进行断句或合并句子来解决。
```
