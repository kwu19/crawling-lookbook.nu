import scrapy
import random
from scrapy.http.request import Request
from ..items import LookbookItem


class LookbookuserSpider(scrapy.Spider):
    name = "lookbookuser"
    # fan_page = 1
    follow_page = 1
    look_page = 1

    COUNT_MAX = 500   # Crawl 500 people's data
    PAGE_MAX = 50
    count = 0

    user_id = 2362237
    user_base_url = 'https://lookbook.nu/user/%s'
    start_urls = [user_base_url % user_id]

    def __init__(self):
        self.personal_info = {'Name': '', 'Country': '', 'n_fans': '', 'n_looks': '', 'n_loves': '', 'n_hypes': '',
                         'n_follow': ''}
        self.general_info = {'ID': '', 'url': '', 'personal_info': self.personal_info, 'fans_list': [], 'follow_list': []}

        self.photo_info = {'photo_url': [], 'title': [], 'likes': [], 'date': [], 'hashtag': [], 'colors': [],
                     'photoitems': []}
        self.wholeurls = []

        self.next_user = ''
        # self.fan_site = ''
        self.follow_site = ''
        self.follow_list = []
        self.user_crawled = ['/renataseptember']

    def parse(self, response):
        items = LookbookItem()
        look_site = response.xpath('//a[@class="image"]/@href').getall()

        # self.fan_page = 1
        self.follow_page = 1

        # We only want those users who have more than 50 pictures posted on their page
        if len(look_site) > 50:
            print(look_site[1])

            # Flush the variables
            self.photo_info = {'photo_url': [], 'title': [], 'likes': [], 'date': [], 'hashtag': [], 'colors': [],
                               'photoitems': []}
            self.personal_info = {'Name': '', 'Country': '', 'n_fans': '', 'n_looks': '', 'n_loves': '', 'n_hypes': '',
                                  'n_follow': ''}
            self.general_info = {'ID': '', 'url': '', 'personal_info': self.personal_info, 'follow_list': []}

            # Get the general information first
            self.general_info['ID'] = response.xpath('//form[@method="post"]/@data-user-id').get()
            self.general_info['url'] = 'https://lookbook.nu/user/' + str(self.general_info['ID'])
            self.personal_info['Name'] = response.xpath('//a[@itemprop="name"]/@title').get()
            self.personal_info['Country'] = response.xpath('//a[contains(@data-track,"country click")]/text()').get()
            total = response.xpath('//span[@class="bigger strong"]/text()').getall()
            self.personal_info['n_fans'] = total[0]
            self.personal_info['n_looks'] = total[1]
            self.personal_info['n_loves'] = total[2]
            self.personal_info['n_hypes'] = total[3]
            self.personal_info['n_follow'] = total[4]
            items['general_info'] = self.general_info

            # self.fan_site = 'https://lookbook.nu' + response.xpath('//a[@name="fans.users"]/@href').get()
            self.follow_site = 'https://lookbook.nu' + response.xpath('//a[@name="fanned.users"]/@href').get()

            # Go to next two pages to crawl their photos and following list
            yield Request('https://lookbook.nu' + str(look_site[1]), callback=self.parse_looks, meta={'item': items})
            # yield Request(self.fan_site, callback=self.parse_fan_page, meta={'item': items})
            yield Request(self.follow_site, callback=self.parse_follow_page, meta={'item': items})
        else:
            # If this person doesn't have enough photos posted, we are going to randomly choose another user
            self.next_user = random.choice(self.follow_list)
            while self.next_user in self.user_crawled:
                self.next_user = random.choice(self.follow_list)
            print(self.next_user)
            self.user_crawled.append(self.next_user)
            yield Request('https://lookbook.nu' + self.next_user, callback=self.parse)

    # def parse_fan_page(self, response):
    #     items = response.meta['item']
    #
    #     fans_id = response.xpath('//a[@class="no_underline"]/@href').getall()[1:]
    #     if fans_id:
    #         for i in fans_id:
    #             self.general_info['fans_list'].append(i)
    #         self.fan_page += 1
    #         if self.fan_page < self.PAGE_MAX:
    #             yield scrapy.Request(self.fan_site + '?page=%s' % self.fan_page, callback=self.parse_fan_page,
    #                                  meta={'item': items})
    #     else:
    #         items['general_info'] = self.general_info
    #         self.fan_page = 1

    def parse_follow_page(self, response):
        '''
        Get the following list that one user has.
        Save the following list in an item dictionary with key general_info.
        '''

        items = response.meta['item']

        following_id = response.xpath('//a[@class="no_underline"]/@href').getall()[1:]

        if len(following_id) < 2 and self.follow_page == 1:   # In case of this user is not following any person
            self.next_user = random.choice(self.follow_list)
            yield Request('https://lookbook.nu' + self.next_user, callback=self.parse)
        elif following_id:   # Go to next page of following list
            for i in following_id:
                self.follow_list.append(i)
                self.general_info['follow_list'].append(i)
            self.follow_page += 1
            if self.follow_page < self.PAGE_MAX:
                yield scrapy.Request(self.follow_site + '?page=%s' % self.follow_page,
                                     callback=self.parse_follow_page, meta={'item': items})
        else:   # Store the following list in dictionary with key general_info
            items['general_info'] = self.general_info
            self.follow_page = 1

    def parse_looks(self, response):
        '''
        Get all the photo information in this function and save it in dictionary with key photo_info.
        Then go to next user's page.
        '''
        items = response.meta['item']

        photo_url = 'http:' + response.xpath('//img[@id="main_photo"]/@src').get()
        title = response.xpath('//div[@class="look-meta-container"]/h1/text()').get().strip()
        likes = response.xpath('//div[@class="hypes-count"]/text()').get()
        date = response.xpath('//meta[@itemprop="dateCreated"]/@content').get()
        hashtag = response.xpath('//p[@id="look_descrip"]/a[@class="hashtag"]/text()').getall()
        colors = response.xpath('//div[@class="color-block"]/@title').getall()
        photoitems = response.xpath('//div[@class="item-name"]/a/text()').getall()
        photoitems = [l.strip() for l in photoitems]
        photoitems = [l for l in photoitems if l]

        self.photo_info['photo_url'].append(photo_url)
        self.photo_info['title'].append(title)
        self.photo_info['likes'].append(likes)
        self.photo_info['date'].append(date)
        self.photo_info['hashtag'].append(hashtag)
        self.photo_info['colors'].append(colors)
        self.photo_info['photoitems'].append(photoitems)

        items['photo_info'] = self.photo_info

        next_page = response.xpath('.//a[@id="next_look"]/@href').extract()
        if next_page:
            next_href = next_page[0]
            next_page_url = 'https://lookbook.nu' + next_href
        if next_page_url not in self.wholeurls:
            self.wholeurls.append(response.request.url)
            request = scrapy.Request(url=next_page_url, callback=self.parse_looks, meta={'item': items})
            yield request
        else:   # Finish crawling all the photos that this user has
            yield items
            self.next_user = random.choice(self.follow_list)    # Get next user id by randomly choosing one from this
                                                                # user's following list
            while self.next_user in self.user_crawled:
                self.next_user = random.choice(self.follow_list)
            print(self.next_user)
            self.user_crawled.append(self.next_user)
            self.count = self.count + 1
            if (self.count < self.COUNT_MAX):
                yield Request('https://lookbook.nu' + self.next_user, callback=self.parse)
