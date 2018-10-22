1.这里尝试自动下载旗米拉论坛的视频数据
2.入口在http://bbs.taiwan123.cn/new/，这个网页上通过/api.php?mod=js&bid=78的JS脚本获取最新节目列表，获取到的结果中有类似
	http://bbs.taiwan123.cn/forum.php?mod=viewthread&tid=74000这样的多个节目链接
3.每个节目链接点击进去会有“微云链接”，“在线播放：”，“网站高清视频无广告”等对应的链接，我们只需要处理“微云链接”
4.微云链接形如https://share.weiyun.com/5UpbGXQ，点击后进入微云的域名
5.微云的网页界面可“保存微云”，也可“下载”
6.


数据库中要收集的信息有
download_time,program_name,file_name,file_size,description