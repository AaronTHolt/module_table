## Written by Aaron Holt
## 02-09-2018
## Script that takes JSON lmod output and makes
## an HTML table to display avaialable modules
## and versions

import json
import os
import subprocess

html_table_file = 'modules.html'

def fix_JSON(json_message=None):
    json_message = json_message.replace('\r\n', '')
    result = None
    try:        
        result = json.loads(json_message)
    except Exception as e:      
        # Find the offending character index:
        idx_to_replace = int(str(e).split(' ')[-1].replace(')', ''))
        # Remove the offending character:
        json_message = list(json_message)
        json_message[idx_to_replace] = ' '
        new_message = ''.join(json_message)     
        return fix_JSON(json_message=new_message)
    return result

def html_table(mylist):
    yield '<table>'
    for sublist in mylist:
        yield '  <tr><td>'
        yield '    </td><td>'.join(sublist)
        yield '  </td></tr>'
    yield '</table>'

def html_table_from_dict(my_dict):
    yield '<table>'
    yield '  <col width="100">'
    yield '  <col width="300">'
    yield '  <col width="500">'
    yield '  <tr>'
    yield '    <th>Name</th>'
    yield '    <th>Versions -- Prerequisites</th>'
    #yield '    <th>Prerequisites</th>'
    yield '    <th>Info</th>'
    yield '  </tr>'

    for key, val in sorted(my_dict.items()):
        if val[0][0][0] is None:
            continue
        yield '  <tr>'
        yield '    <td>{module}</td>'.format(module=key)
        sorted_versions = val[0]
        sorted_string = '<p>'
        if len(val[0]) > 1:
            sorted_versions.sort(key=lambda x: (x[0], x[1]))
        for version in sorted_versions:
            sorted_string += version[0]
            sorted_string += ' -- '
            if version[1] is not '' or version[1] is not None:
                sorted_string += version[1]
            else:
                sorted_string += 'None'
            sorted_string += '</p>'

        yield '    <td>{ver}</td>'.format(ver=sorted_string)
        yield '    <td>{info}</td>'.format(info=val[1])
        yield '  </tr>'

    yield '</table>'



data = []
table = []
module_dict = {}
modulepaths = os.environ['MODULEPATH']
modulepaths = modulepaths.split(':')


for ii, cur_path in enumerate(modulepaths):
    cur_json_file = '{counter}.json'.format(counter=ii)
    output = subprocess.check_output(['/curc/sw/lmod/6.3.7/libexec/spider', '-o', 'spider-json', cur_path]) #, '>', cur_json_file])

    data = fix_JSON(output.decode("utf-8"))

    for key, val in data.items():
        for key2, val2 in data[key].items():
            module_name = ''
            module_ver = ''
            if data[key][key2].get('full') is not None:
                module_name = data[key][key2].get('full').split('/')[0]
                if '/' in data[key][key2].get('full'):
                    module_ver = data[key][key2].get('full').split('/')[1]
                else:
                    module_ver = None

            if module_name in module_dict:
                module_dict[module_name][0].append([module_ver, data[key][key2].get('parent', None)[0].replace("default:","").replace("default", "")])
            else:
                module_dict[module_name] = [[[module_ver, data[key][key2].get('parent', None)[0].replace("default:","").replace("default", "")]], 
                        data[key][key2].get('help', '\n').replace('\n', ' ')]

            table.append([data[key][key2]['full'], 
                data[key][key2]['parent'][0].replace("default","").replace(":", ""), 
                data[key][key2].get('help', '\n').replace('\n', ' ')])

table.sort(key=lambda x: x[0])

mytable = (u'\n'.join(html_table(table))).encode('utf-8')

#with open(html_table_file, 'wb') as f:
#    f.write(mytable)
#    f.close()
#
#print("HTML table written to:", html_table_file)

mytable2 = (u'\n'.join(html_table_from_dict(module_dict))).encode('utf-8')

with open(html_table_file, 'wb') as f:
    f.write(mytable2)
    f.close()

print("HTML table written to:", html_table_file)
