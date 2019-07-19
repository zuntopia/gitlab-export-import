import gitlab
import os
import sys
import time

from gitlab.exceptions import GitlabGetError

EXPORT = sys.argv[1]
EXP_TOKEN = sys.argv[2]
IMPORT = sys.argv[3]
IMP_TOKEN = sys.argv[4]

old_gitlab = gitlab.Gitlab(EXPORT, private_token=EXP_TOKEN)
new_gitlab = gitlab.Gitlab(IMPORT, private_token=IMP_TOKEN)

with open('projects', 'rb') as f:
    namespaces = []
    for project in f.readlines():
        project = project[:-1]

        op = old_gitlab.projects.get(project)

        try: 
            check = new_gitlab.projects.get(project)
            print "project pass %s" % project
            continue
        except GitlabGetError:
            pass
        except:
            print "unknown error %s " project

        export = op.exports.create({})
        export.refresh()

        while export.export_status != 'finished':
            time.sleep(1)
            export.refresh()

        namespace = '/'.join(project.split('/')[:-1])
        project_path = project.split('/')[-1]
        
        with open('export.tar.gz', 'wb') as w:
            export.download(streamed=True, action=w.write)
        
        output = new_gitlab.projects.import_project(open('./export.tar.gz', 'rb'), project_path, namespace=namespace)
        project_import = new_gitlab.projects.get(output['id'], lazy=True).imports.get()
        while project_import.import_status != 'finished':
            time.sleep(1)
            project_import.refresh()
