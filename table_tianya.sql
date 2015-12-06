CREATE TABLE IF NOT EXISTS `reply` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增ID',
  `title_id` int(11) NOT NULL COMMENT '标题ID',
  `author` varchar(255) NOT NULL COMMENT '回复者',
  `time` datetime default NULL COMMENT '回复时间',
  `text` text NOT NULL COMMENT '回复内容',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8;


create table if not exists titles(
`id` int(11) not null primary key auto_increment comment '自增id',
`reply_num` int(11) not null comment '回复数量',
`click_num` int(11) not null comment '点击数',
`author` varchar(255) not null comment '作者',
`time` datetime default NULL comment '日期',
`link` varchar(255) not null comment '链接',
`text` text not null comment '内容'
)ENGINE=InnoDB  DEFAULT CHARSET=utf8;
