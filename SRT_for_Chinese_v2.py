'''
SRT_for_Chinese 2.0
Author:kindkind.com

脚本编写于 python 3.7

说明：
谷歌云服务及SRT转换均参考了该项目：https://github.com/darshan-majithiya/Generate-SRT-File-using-Google-Cloud-s-Speech-to-Text-API.git
使用过程中发现，对于上面项目中仅仅按照时间段分割英语单词的方式，非常不适合中国人以字为单位的语言习惯，
经过反复测试修改，始终有语句中断错乱、时码偏差较大的问题，
最后干脆将分割方式按照我的预想进行了重写，并添加了自动判断发音习惯参考值的功能（比较简陋，但是可以自适应不同人的语速了），
现在的版本是我正在使用，感觉比较良好的一个版本，现只分享出转换SRT字幕部分的代码，
完整的谷歌云语音识别服务的上传、接收脚本，请参考上面的项目。

已知问题：
1.鉴于谷歌声音识别服务的一些缺陷（个人感觉是谷歌开发人员不怎么用这个服务吧）转换出来的内容，会分为几个段落，
  SRT转换以后，对于每段最后一个字的时长无法与下一段落的起始字时间对接，导致每个段落最后一句显示的时长不够。
  现将毫秒数x2以便不至于过短，我也懒得继续尝试，反正还需要用字幕软件校对一遍内容及部分时码。
2.语音识别服务产生的时码，跟音频时码有偏差，基本上整体会慢不到1秒（也有部分句子时码刚好），
  使用SRT字幕编辑软件进行整体提前修正即可。
3.因为没有使用单词模型进行对照断句（感觉个人使用，弄个模型库不太现实），有些字说的快的时候会出现超长的句子，
  而有些字又会超短，当然也跟语音识别服务的时码缺陷有关，暂时无法解决，只有字幕软件校对进行断句或合并句子来解决。
'''
#coding=utf8
import sys,os
import datetime,time
import srt
from pprint import pprint


##############################################################
def wordSpeed(result):	# 计算发音习惯，统计单字速度，得出平均值阈值
	wn = 0
	wCount = 0
	wBalance = 0
	wMax = 0
	for i in range(len(result.alternatives[0].words) - 1):
		wStart = int((result.alternatives[0].words[i].start_time.seconds + result.alternatives[0].words[i].start_time.nanos*0.001*0.001*0.001)*100)
		wEnd = int((result.alternatives[0].words[i].end_time.seconds + result.alternatives[0].words[i].end_time.nanos*0.001*0.001*0.001)*100)
		wt = wEnd-wStart
		
		if wt<80: #过滤超长的
			wn += 1 #统计字数
			wMax = wMax if wMax>wt else wt
			wCount += wt
			##print(wn,result.alternatives[0].words[i].word," : ",wStart,wEnd," = ",wEnd-wStart)
			if wn>200 : #限制取样数量
				break
		##time.sleep(0.5)

	if wn:
		wBalance = int(wCount / wn)
		print("平均：",wBalance, "    最大：",wMax)
		print(" = "*20)
	
	return wBalance , wMax


##############################################################
def subtitle_generation(speech_to_text_response):	# 转SRT过程
	response = speech_to_text_response
	transcriptions = []
	index = 0

	sclip = 1
	##tNum = 1
	
	for result in response.results:
		try:
			start_sec = 0
			start_microsec = 0
			
			# for last word of result
			last_word_end_sec = result.alternatives[0].words[-1].end_time.seconds
			last_word_end_microsec = result.alternatives[0].words[-1].end_time.nanos * 0.001
			
			# bin transcript
			transcript = "" #result.alternatives[0].words[0].word
			
			##index += 1 # subtitle index
			
			wBalance, wMax = wordSpeed(result) #计算发音习惯
			whold = int((wMax+wBalance)/2) #断句阈值

			for i in range(len(result.alternatives[0].words)):
				try:
					if i==0 :
						word=""
					else:
						word = result.alternatives[0].words[i-1].word
					##if i==len(result.alternatives[0].words)-1 : word += result.alternatives[0].words[i].word

					if 0==len(transcript) :
						start_sec = result.alternatives[0].words[i].start_time.seconds
						start_microsec = result.alternatives[0].words[i].start_time.nanos * 0.001
					word_start_sec = result.alternatives[0].words[i].start_time.seconds
					word_start_microsec = result.alternatives[0].words[i].start_time.nanos * 0.001 # 0.001 to convert nana -> micro 毫微秒转换微秒microsecond
					word_end_sec = result.alternatives[0].words[i].end_time.seconds
					word_end_microsec = result.alternatives[0].words[i].end_time.nanos * 0.001
					##print(f"{start_sec}\t-\t{word_end_sec}\t{word}")
					##pprint()
					##print("")
					
					transcript += word
					##print(f"{i}/{len(result.alternatives[0].words)-1}\t{word_start_sec},{'%6.1f' % word_start_microsec}\t-\t{word_end_sec},{'%6.1f' % word_end_microsec}\t\t{word}")
					
					#################### 按照标点断句 #########################
					"""tt = result.alternatives[0].transcript
					if tt[i+tNum:i+1+tNum]=="。" or tt[i+tNum:i+1+tNum]=="！" : ## or tt[i+tNum:i+1+tNum]=="，" or tt[i+tNum:i+1+tNum]=="、"
						tNum += 1
						if len(transcript)<4 :
							transcript += " "
						else :
							sclip = 0
					"""
					##print(i,tNum,tt[i+tNum:i+1+tNum],result.alternatives[0].words[i + 1].word,transcript)
					#################### 按照停顿断句 #########################
					wThis = int((result.alternatives[0].words[i].start_time.seconds + result.alternatives[0].words[i].start_time.nanos*0.001*0.001*0.001)*100)
					wEnd = int((result.alternatives[0].words[i].end_time.seconds + result.alternatives[0].words[i].end_time.nanos*0.001*0.001*0.001)*100)
					wt = wEnd - wThis
					##print(" "*20,int((wNext-wThis)*100))
					
					if wt>wMax : sclip = 0 #间隔过长断句
					if sclip>0 and wt>whold and len(transcript)>3 : sclip = 0 #阈值断句
					if sclip>0 and wt>wBalance and len(transcript)>10 : sclip = 0 #长度过长断句
					
					##print(" "*20,"Len = ",len(result.alternatives[0].words))
					##time.sleep(0.5)
					#################### 自定义规则结束 #######################
					if sclip == 0 or i==len(result.alternatives[0].words)-1:
						
						previous_word_end_sec = result.alternatives[0].words[i].end_time.seconds
						previous_word_end_microsec = result.alternatives[0].words[i].end_time.nanos * 0.001
						
						# append bin transcript
						if i>=len(result.alternatives[0].words)-1 :
							transcript += result.alternatives[0].words[i].word
						else:
							index += 1
							transcriptions.append(srt.Subtitle(index, datetime.timedelta(0, start_sec, start_microsec), datetime.timedelta(0, previous_word_end_sec, previous_word_end_microsec), transcript))
							##print(f"{index}\t{start_sec},{'%6.1f' % start_microsec}\t-\t{previous_word_end_sec},{'%6.1f' % previous_word_end_microsec}\t\t{transcript}")
							transcript = ""
							
						sclip = 1
						##pprint(transcriptions)
						##print(f"{start_sec}\t-\t{previous_word_end_sec}\t{transcript}\n")
						
						###start_sec = word_start_sec
						###start_microsec = word_start_microsec
						
						##print(" "*20,transcript)
						
						##time.sleep(3)
						
						
				except IndexError as e:
					pass
					print("Err1:",e," ?? "*10)
					print('文件', e.__traceback__.tb_frame.f_globals['__file__'], '行号', e.__traceback__.tb_lineno)
				##time.sleep(0.05)
			##tNum = 1
			# append transcript of last transcript in bin
			index += 1
			transcriptions.append(srt.Subtitle(index, datetime.timedelta(0, start_sec, start_microsec), datetime.timedelta(0, last_word_end_sec, last_word_end_microsec*2), transcript))
			##pprint(transcriptions)
			##print("最后一句 ",f"{index}\t{start_sec},{'%6.1f' % start_microsec}\t-\t{last_word_end_sec},{'%6.1f' % last_word_end_microsec}\t\t{transcript}")
			##time.sleep(5)
		except IndexError as e:
			pass
			print("Err2:",e," ?? "*10)
			print('文件', e.__traceback__.tb_frame.f_globals['__file__'], '行号', e.__traceback__.tb_lineno)

	print(f"SRT Index-Count :{index-1}")
	# turn transcription list into subtitles
	subtitles = srt.compose(transcriptions)
	return subtitles



if __name__ == '__main__':
	##调用及保存SRT字幕
	subtitles = subtitle_generation(response)
	timer = 1 ##str(time.strftime("%Y%m%d_%H%M%S",time.localtime()))

	with open(f"subtitles_{timer}.srt", "w") as f:
		f.write(subtitles)


