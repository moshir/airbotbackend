import pprint
import json
template = {
  "Version":"2012-10-17",
  "Statement":[
    {
      "Sid":"AddCannedAcl",
      "Effect":"Allow",
      "Principal": {"AWS": ["arn:aws:iam::950130011294:root"]},
      "Action":["s3:PutObject","s3:PutObjectAcl"],
      "Resource":["arn:aws:s3:::bucketpolicylimit/*"]
    }
  ]
}



print len(str(template))
nbprincipal = 0
accountid = 111122223333
principaltpl = "arn:aws:iam::950130011294:root"
while len(json.dumps(template)) < 19*1000 :
    principal = principaltpl%vars()
    template["Statement"][0]["Principal"]["AWS"].append(principal)
    nbprincipal +=1


#nbprincipal 239
print nbprincipal

#policy size 19007
print len(json.dumps(template))


#policy body

print json.dumps(template)



inline_policy_limit = 2048
template = {
  "Version":"2012-10-17",
  "Statement":[
    {
      "Sid":"AddCannedAcl",
      "Effect":"Allow",
      "Principal": {"AWS": ["arn:aws:iam::950130011294:root"]},
      "Action":["s3:PutObject","s3:PutObjectAcl"],
      "Resource":[]
    }
  ]
}

nbdataset = 0
while  len(json.dumps(template).replace(" ",""))< inline_policy_limit :
    template["Statement"][0]["Resource"].append(
        "arn:aws:s3:::bucketpolicylimit/datasetname"
    )
    nbdataset += 1


print "nb datasets in inline policy = ", nbdataset