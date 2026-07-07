import glob, os, re
files = glob.glob('dashboard/*.py') + glob.glob('dashboard/pages/*.py')
for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    new_content = re.sub(r'# TODO:.*?\n\s*\"\"\"[\s\S]*?\"\"\"\n', '', content)
    
    with open(f, 'w', encoding='utf-8') as file:
        file.write(new_content)
print('Fixed', len(files), 'files')
