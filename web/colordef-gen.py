# uses web.py

import web
from web import form
import colordefs
import json
import os

urls = (
    '/', 'index',
    '/publish', 'publish'
)

render = web.template.render('templates/')

mydir = os.path.dirname(os.path.realpath(__file__))

app = web.application(urls, globals())

myform = form.Form( 
    form.Textbox("name", description="name"), 
    form.Textbox("unit", descrptions = "satoshi per unit"),
    form.Dropdown('style', ['genesis', 'address']),
    form.Textarea('data', description="<txhash>:<outindex>, one per line. or address hash"),
    form.Textbox("publickey", description = "public key (optional)"))
    

def colordef_from_form(form):
    x = {"name": form.d.name,
         "unit": form.d.unit,
         "metaprops": ["name", 'unit'],
         "style": form.d.style}
    if form.d.publickey:
        x["publickey"] = form.d.publickey
        x['metaprops'].append("publickey")
    if form.d.style == "genesis":
        issues = []
        for line in form.d.data.splitlines():
            [txhash, outindex] = line.split(':')
            issues.append({"txhash": txhash.strip(), "outindex": int(outindex)})
            x['issues'] = issues
    elif form.d.style == "address":
        x['address_pkhash'] = data.strip()
    else:
        raise Exception("unknown color defintion style")
    colordefs.FinalizeColorDefinition(x)
    if not colordefs.ValidateColorDefinition(x):
        raise Exception("somehow validation failed")
    return x

def save_colordef(cd):
    colorid = cd['colorid']
    fname = colorid + '.colordef'
    path = os.path.join(mydir, 'static', 'colordefs', fname)
    if os.path.exists(path):
        raise Exception("already exists")
    with open(path, "w") as f:
        json.dump([cd], f, indent = True)

class index:        
    def GET(self):
        form = myform()
        return render.formtest(form)
    def POST(self): 
        form = myform() 
        if not form.validates(): 
            return render.formtest(form)
        else:
            cd = None
            try:
                cd = colordef_from_form(form)
            except Exception as e:
                return "There was an error: %s" % e
            try:
                save_colordef(cd)
            except Exception as e:
                return "Could not save your color definition: %s" % e
            url = "/static/colordefs/%s.colordef" % cd['colorid']
            return "<a href='%s'>%s</a>" % (url, cd['colorid'])

class publish:
    def POST(self):
        data = web.webapi.data()
        colordef = None
        try:
            colordef = json.loads(data)[0]
        except Exception as e:
            return "Error parsing data: %s" % e
        try:
            if not colordefs.ValidateColorDefinition(colordef):
                return "Error: failed to validate"
        except Exception as e:
            return "Error validating: %s" % e
        try:
            save_colordef(colordef)
        except Exception as e:
            return "Error saving: %s" % e
        return "OK"
            

if __name__ == "__main__":
    app.run()
