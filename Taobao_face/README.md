# 爬取商品列表



## (1)找到用户信息
清除cookies，访问https://login.taobao.com/member/login.jhtml?redirectURL=http%3A%2F%2Fs.taobao.com%2Fsearch%3Fq%3Diphone

点击登录，用浏览器或抓包工具找到下图所示url，复制相关用户信息

<img src="https://img-blog.csdnimg.cn/2020082921393077.jpg">

## (2)填写信息

<img src="https://img-blog.csdnimg.cn/20200829214101408.jpg">


## (3)说明
在命令行中输入
`
python run.py -h
`
查看相关参数

<img src="https://img-blog.csdnimg.cn/202008292128128.jpg">

## (4)运行
`
python run.py product
`

<img src="https://img-blog.csdnimg.cn/20200829213558210.jpg">

## (5)结果

<img src="https://img-blog.csdnimg.cn/20200829215134520.jpg">

## (6)

如有问题可以查看，[爆肝一下午的CSDN博客链接](https://blog.csdn.net/pineapple_C/article/details/108181761)

欢迎提出问题
