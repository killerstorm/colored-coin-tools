import hashlib

def sha256(bits):
   return hashlib.new('sha256', bits).digest()
def ripemd160(bits):
    return hashlib.new('ripemd160', bits).digest()
def hash160(bits):
    return ripemd160(sha256(bits))

def binary_to_hex(b):
    return b.encode('hex_codec')
def hex_to_binary(b):
    return b.decode('hex_codec')

def ComputeColorMetaHash(props):
   metahash = ""
   metaprops = props.get("metaprops", [])
   if metaprops:
       meta_list = []
       for mn in metaprops:
           mv = props[mn]
           if isinstance(mv, (int, long)):
               mv = str(mv)
           if not isinstance(mv, (str, unicode)):
               raise Exception("ComputeColorID: meta data must be string or integer")
           mv = mv.encode("utf-8")
           mn = mn.encode("utf-8")
           meta_list.append(mn)
           meta_list.append(mv)
       meta = ':'.join(meta_list)
       print meta
       metahash = binary_to_hex(hash160(meta.encode("utf-8")))
   return metahash    

def ComputeColorID(props):

   contracthash = props.get("contracthash", "")
   style = props["style"]
   previousid = props.get("previousid", "")
   metahash = props.get("metahash", "")

   data_list = []
   if style == "genesis":
      for issue in props["issues"]:
         data_list.append(issue["txhash"])
         data_list.append(str(issue["outindex"]))
   elif style == "address":
      data_list.append(props["address_pkhash"])
   else:
      raise Exception("unknown colordef style")

   data = ':'.join(data_list)

   #optional meta-data gets hashed too
   contents = ':'.join([metahash, previousid, contracthash, style, data])

   definition_string =  "colordef:%s:colordef" % contents

   print definition_string

   return binary_to_hex(hash160(definition_string.encode("utf-8")))

def FinalizeColorDefinition(x):
    metahash = ComputeColorMetaHash(x)
    if metahash:
        x['metahash'] = metahash
    x['colorid'] = ComputeColorID(x)
    return x

def ValidateColorDefinition(props):
    metahash = ComputeColorMetaHash(props)
    if metahash != props.get("metahash", ""):
        print "metahash is invalid"
        return False
    computedColorID = ComputeColorID(props)
    if computedColorID != props['colorid']:
        print "colorid is invalid"
        return False
    # TODO: validate signatures and stuff
    return True

def test1():
    x = {
        'colorid': '0317f45a20a98606f3148faf7dbe882a58f96f15',
        'name': "TESTcc", 
        'style': "genesis",
        'issues': [{'txhash': "c26166c7a387b85eca0adbb86811a9d122a5d96605627ad4125f17f6ddcbf89b", "outindex": 0}]
        }
    return ValidateColorDefinition(x)

def test2():
    x = {
        'metaprops': ['name', 'unit'],
        'unit': 1000,
        'name': "TESTcc", 
        'style': "genesis",
        'metahash': '4d24940a40f0b34d363e3878ff24013ba80af840',
        'colorid': '453b5409513e2a5fa0450b61a2c5ea72bbbdb260',
        'issues': [{'txhash': "c26166c7a387b85eca0adbb86811a9d122a5d96605627ad4125f17f6ddcbf89b",
                    "outindex": 0}]
        }
    return ValidateColorDefinition(x)
