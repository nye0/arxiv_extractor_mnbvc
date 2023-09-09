import os
import glob
import re

import re

def remove_comments(tex_content):
    # Regular expression pattern for LaTeX comments
    comment_pattern = re.compile(r'(?<!\\)%.*?$', flags=re.MULTILINE)
    return comment_pattern.sub('', tex_content).strip()
    
def begin_end_extractor(tex_content, what='figure'):
    # figure/table/equation
    pattern1 = re.compile(rf'\\begin\{{{what}\}}.*?\\end\{{{what}\}}', re.DOTALL)
    pattern2 = re.compile(rf'\\begin\{{{what}\*}}.*?\\end\{{{what}\*}}', re.DOTALL)
    extracted1 = pattern1.findall(tex_content)
    extracted2 = pattern2.findall(tex_content)
    return extracted1 + extracted2
#todo: add caption/ 
def extract_labels(tex_content):
    # Regular expression pattern to find all \label{...} entries
    label_pattern = re.compile(r'\\label\{(.*?)\}')
    return label_pattern.findall(tex_content,re.DOTALL)


def block_spliter(tex_content):
   
    # Split by major blocks while keeping the delimiter (i.e., the block)
    block_pattern = re.compile(r'(\\begin\{(.*?)\}.*?\\end\{\2\})', re.DOTALL)
    blocks = re.split(block_pattern, tex_content)

    # Process each segment: if it's not a block, split it by empty lines
    # todo: paragraph split more robust
    processed_blocks = []
    for block in blocks:
        if block.strip() and not block_pattern.match(block):
            subblocks = re.split(r'\n\s*\n', block)  # Split by empty lines
            processed_blocks.extend([sub.strip() for sub in subblocks if sub.strip()])
        elif block.strip():
            processed_blocks.append(block.strip())
            
    return processed_blocks



def list_tex_files(root_folder):
    # 使用os.path.join确保路径在所有操作系统上都有效
    pattern = os.path.join(root_folder, '**', '*.[tT][eE][xX]')
    
    # 使用glob.glob搜寻所有匹配的文件。注意recursive=True是必要的，以搜索所有子文件夹
    tex_files = glob.glob(pattern, recursive=True)

    return tex_files


def filter_tex_file(tex_file):
    # 筛选.tex文件是否保留
    filename = os.path.basename(tex_file)
    
    # 根据文件名判断
    name_check = ["main", "Main", "MAIN", "paper", "Paper"]
    if any(name in filename for name in name_check):
        return True
    
    # 根据文件内容判断
    tags = ["\\title", "\\section", "\\subsection"]
    with open(tex_file, 'r', encoding='utf-8') as file:
        for line in file:
            if any(line.strip().startswith(tag) for tag in tags):
                return True
    return False
