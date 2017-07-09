CREATE TABLE IF NOT EXISTS  imp(datum text, tid text, vindriktning varchar(10), kvalitet varchar(10) ,vindhastighet varchar(10), kvalitet2 varchar(10), station varchar(10) );

.separator ,
.import cleaned.csv imp
