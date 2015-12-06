CREATE TABLE IF NOT EXISTS `gzrb_titles` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增ID',
  `link` varchar(255) NOT NULL COMMENT '链接',
  `title` varchar(255) NOT NULL COMMENT '标题',
  `text` text NOT NULL COMMENT '回复内容',
  `time` datetime default NULL COMMENT '回复时间',
  `click_num` int(11) DEFAULT NULL COMMENT '点击数',
  `reply_num` int(11) DEFAULT NULL COMMENT '回复数',
  PRIMARY KEY (`id`)
)AUTO_INCREMENT = 102000000, ENGINE=InnoDB  DEFAULT CHARSET=utf8;
