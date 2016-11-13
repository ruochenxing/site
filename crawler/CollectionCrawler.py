# -*- coding:utf-8 -*-

from QuestionImageCrawler import *
from util import *
import sys

# 收藏夹的地址
COLLECTION_URL = 'https://www.zhihu.com/collection/{id}?page='
logger = get_logger(__file__)

reload(sys)
sys.setdefaultencoding('utf-8')


class CollectionCrawler(BaseCrawler):
	def __init__(self, linkId, pageStart, pageEnd):
		super(CollectionCrawler, self).__init__()
		self._pageStart = int(pageStart)
		self._pageEnd = int(pageEnd) + 1
		self._linkId = linkId
		self.downLimit = 0  # 低于此赞同的答案不收录

	def start(self):
		for page in range(self._pageStart, self._pageEnd):  # 收藏夹的页数
			url = COLLECTION_URL.format(id=self._linkId) + str(page)
			content = self.get(url)
			if content is None:
				logger.error("爬取失败" + url + "\ncontent =" + content)
				continue
			soup = BeautifulSoup(content)

			answerlist = soup.find_all("div", class_="zm-item-answer  zm-item-expanded")
			if answerlist is not None and len(answerlist) > 0:
				for ans in answerlist:
					answer = AnswerParser(ans).parse_imgs()
					if not answer:
						continue
					AnswerParser.save(answer)

			questionlist = soup.find_all('div', class_='zm-item')
			for question in questionlist:  # 收藏夹的每个问题
				qtitle = question.find('h2', class_='zm-item-title')
				if qtitle is None:  # 被和谐了
					continue
				linkid = qtitle.a['href'][1 + qtitle.a['href'].rfind('/'):]
				q = select_one(QUESTION_COLL, {'_id': str(linkid)})
				if q is not None:
					print QUESTION_URL.format(id=linkid), "已经爬取过了"
					continue
				logger.info("begin url " + qtitle.a['href'])
				question_crawler = QuestionCrawler()
				question_crawler.run(str(linkid))
				logger.info("finished url " + qtitle.a['href'])
				pause(10)
