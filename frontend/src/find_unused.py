import os
import glob
import re

def find_unused_files(root_dir):
    ts_files = glob.glob(os.path.join(root_dir, '**', '*.ts'), recursive=True)
    tsx_files = glob.glob(os.path.join(root_dir, '**', '*.tsx'), recursive=True)
    all_files = ts_files + tsx_files

    # Read all contents
    contents = []
    for f in all_files:
        with open(f, 'r', encoding='utf-8') as file:
            contents.append(file.read())
    
    all_content_str = "\n".join(contents)
    
    unused = []
    for f in all_files:
        base_name = os.path.splitext(os.path.basename(f))[0]
        if base_name in ['main', 'App', 'vite-env.d']:
            continue
        
        # Count occurrences of base_name
        count = len(re.findall(r'\b' + re.escape(base_name) + r'\b', all_content_str))
        
        # If it only occurs once (its own definition/export)
        if count <= 1:
            unused.append(f)
            
    return unused

if __name__ == '__main__':
    unused = find_unused_files('.')
    for u in unused:
        print(u)
