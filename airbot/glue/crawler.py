import pprint
import boto3
from airbot import errors
from datetime import datetime
from airbot.logger import logger

class Crawler:
    @classmethod
    def glue(cls):
        return boto3.client('glue', region_name="eu-west-1")

    @classmethod
    def delete(cls, **kwargs):
        try :
            cls.glue().delete_crawler(
                Name=kwargs["name"]
            )
        except Exception :
            return

    @classmethod
    def get(cls,**kwargs):
        try :
            response = cls.glue().get_crawler(
                Name=kwargs["name"]
            )
            return response["Crawler"]
        except Exception ,e:
            return None

    @classmethod
    def create(cls,**kwargs):
        #ts = datetime.now().strftime("%Y%m%d%H%M%S")
        #db = kwargs["database"]
        #name = "airbot%(db)s%(ts)s" % vars()
        #kwargs.update({"name" : name})

        client = cls.glue()
        targets = {
            'S3Targets': [
                {
                    'Path': 's3://%(bucket)s'%kwargs + ("/%(prefix)s"% kwargs if "prefix" in kwargs.keys() else "")
                }
            ]
        }
        try :
            logger().info("Creating crawler `%s` for bucket `%s` path `%s` and updating database `%s`",kwargs["name"],kwargs["bucket"],kwargs.get("prefix","*"),kwargs["database"])
            response = client.create_crawler(
                Name=kwargs["name"],
                Role="arn:aws:iam::950130011294:role/service-role/AWSGlueServiceRole-airbot",
                DatabaseName=kwargs["database"],
                #Schedule='cron(* /5 * * * *)',
                Description='Crawler for database %(database)s'%kwargs,
                Targets= targets
            )
            return response
        except Exception ,e:
            logger().error("Following error occured when creating crawler %s",str(e))
            return {
                "success" : False,
                "data" : e
            }


    @classmethod
    def start(cls,**kwargs):
        logger().info("Starting Crawler %s ",kwargs["name"])
        client = cls.glue()
        return client.start_crawler(
            Name=kwargs["name"]
        )

    @classmethod
    def crawl_bucket(cls,**kwargs):
        db = kwargs["database"]
        ts = datetime.now().strftime("%Y%m%d%H%M%S")
        name = "airbot%(db)s%(ts)s" % vars()
        kwargs.update({"name" : name})
        cls.create(**kwargs)
        cls.start(**kwargs)
        return name


if __name__=="__main__" :
    k=Crawler.crawl_bucket(**{
        "database" : "mybot",
        "bucket" : "airbot2018",
        "force" : True
    })
    print k
    logger().info("Crawler %s", str(Crawler.get(name="airbotmybot20180922185001")))

    #Crawler.delete(name=k)
