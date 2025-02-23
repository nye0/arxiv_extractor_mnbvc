import os
import tarfile
from tqdm import tqdm
import json

import chardet

from utils import list_tex_files, filter_tex_file


RAW_PATH = "arxiv-subset-100"
PARSE_PATH = "parse"
OUTPUT_TEX_PATH = 'tex.jsonl'


def write_to_jsonl(tex_filelist):
    with open(OUTPUT_TEX_PATH, 'a', encoding='utf-8') as f_out:
        for tex_file in tex_filelist:
            with open(tex_file, 'rb') as f:
                encoding = chardet.detect(f.read())['encoding']
                
            with open(tex_file, 'r', encoding=encoding) as f_tex:
                content = f_tex.read()
                
                id_path = os.path.relpath(tex_file, PARSE_PATH)
                data = {
                    "id": id_path,
                    "text": content
                }
                
                json_line = json.dumps(data)
                f_out.write(json_line + '\n')

def extract_tex(arxiv_parse_path):
    # 找到所有.tex文件
    tex_filelist = list_tex_files(arxiv_parse_path)
    # 过滤有意义的.tex文件
    assert len(tex_filelist) > 0, "没有.tex文件"
    if len(tex_filelist) > 1:
        tex_filelist = list(filter(filter_tex_file, tex_filelist))
    write_to_jsonl(tex_filelist)


def extract_one_arxiv(id):
    """
    提取一个arxiv_id的所有内容
    """
    is_success = None
    arxiv_path = os.path.join(RAW_PATH, id)
    arxiv_parse_path = os.path.join(PARSE_PATH, id)
    os.makedirs(arxiv_parse_path, exist_ok=True)
    pdf_path = os.path.join(arxiv_path, "pdf", id+".pdf")
    source_file_path = os.path.join(arxiv_path, "source", id)
    source_file_path_gz = source_file_path + ".tar.gz"

    # 重命名压缩包
    if os.path.exists(source_file_path):
        os.rename(source_file_path, source_file_path_gz)

    # 检查文件完整性
    if (not os.path.exists(pdf_path)) or (not os.path.exists(source_file_path_gz)):
        print(id + "文件不完整")
        is_success = False

    # 解压
    try:
        with tarfile.open(source_file_path_gz, 'r:gz') as tar_ref:
            tar_ref.extractall(arxiv_parse_path)

        # 1.解析代码
        extract_tex(arxiv_parse_path)

        # 2.解析图文
        is_success = True
    except tarfile.InvalidHeaderError as e:
        print(id, e)
        is_success = False
    finally:
        # 复原压缩包
        if os.path.exists(source_file_path_gz):
            os.rename(source_file_path_gz, source_file_path)
        return is_success


def main():
    os.makedirs(PARSE_PATH, exist_ok=True)
    arxiv_ids = [d for d in os.listdir(RAW_PATH) if os.path.isdir(os.path.join(RAW_PATH, d))]
    arxiv_ids = arxiv_ids#[:10]
    success = 0
    for arxiv_id in tqdm(arxiv_ids):
        if extract_one_arxiv(arxiv_id):
            success += 1
    print("total: {}, success: {}, ratio: {}%,".format(len(arxiv_ids), success, success/len(arxiv_ids)*100.0))


if __name__ == "__main__":
    main()