# daiguangwang.top

---
执行：
python site.py 8080 启动web服务

[知乎带逛]
执行：
python question_crawler1.py 爬取问题下的回答图片 问题ID mongo
python zhihu_collection_spider.py 根据收藏夹爬取其下所有问题的图片 起始页 mongo

[知乎热门问题]
执行init.sql 初始化所有的topic
python topic_crawler2.py 	根据数据库中已有的topic并获取其话题下的question 	mysql 执行前确认是否需要代理 无需登录
python question_crawler2.py 更新已有问题的动态								mysql 执行前确认是否需要代理 无需登录