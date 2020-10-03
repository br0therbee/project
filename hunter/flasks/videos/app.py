# -*- coding: utf-8 -*-
# @Author      : BrotherBe
# @Time        : 2020/10/2 10:54
# @Version     : Python 3.8.5
from flask import Flask, request, render_template

from public import RabbitMQQueue, FrontEndPort
from utils import LogManager, RabbitMQProducer

app = Flask(__name__)
logger = LogManager('videos_flask').file()
producer = RabbitMQProducer(RabbitMQQueue.video_download_name, use_filter=True)


@app.route('/videos/add', methods=['GET'])
def add_form():
    return '''
        <body bgcolor="DodgerBlue">
        <div style="text-align:center">
        <font></font><br/><font></font><br/><font></font><br/>
        <font face="宋体" size="+5" color="#F0F8FF">添加影片链接</font><br/>
        <font></font><br/>
        <font></font><br/>
        <form action ='/videos/add' method='post'>
            <input type="txt"  rows="2" cols="60" placeholder="请输入影片链接...."  
            name='play_url' style="height:40px;width:500px;">  
            <button type="submit" class="search-submit"
            style="height:38px;width:60px;">添加</button> 
        </form>
        </div>
        '''


@app.route('/videos/add', methods=['POST'])
def add():
    play_url = request.form['play_url'].strip()
    logger.info(f'{play_url=}')
    if play_url:
        producer.publish({'play_url': play_url})
        return render_template('add.html', tips=f"添加成功影片链接：{play_url}")
    else:
        return render_template('add.html', tips="请输入正确的影片链接")


if __name__ == '__main__':
    app.run("0.0.0.0", FrontEndPort.video)
