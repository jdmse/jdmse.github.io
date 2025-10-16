import re
import os
from pathlib import Path

def parse_publication_entry(lines):
    """
    解析一个出版物条目,返回序号、标题、作者和其他信息
    """
    # 第一行包含序号和标题
    first_line = lines[0].strip()
    
    # 中文数字映射 - 使用c前缀避免覆盖英文条目
    chinese_numbers = {'一': 'c1', '二': 'c2', '三': 'c3', '四': 'c4', '五': 'c5', 
                      '六': 'c6', '七': 'c7', '八': 'c8', '九': 'c9', '十': 'c10'}
    
    # 尝试匹配阿拉伯数字
    match = re.match(r'^(\d+)\.\s+(.+)$', first_line)
    is_chinese = False
    
    # 如果阿拉伯数字不匹配,尝试匹配中文数字(可能有前导空格)
    if not match:
        match = re.match(r'^\s*([一二三四五六七八九十]+)：(.+)$', first_line)
        if match:
            is_chinese = True
            chinese_num = match.group(1)
            # 转换中文数字为带c前缀的数字,避免覆盖英文条目
            number = chinese_numbers.get(chinese_num, 'c' + chinese_num)
        else:
            return None
    else:
        number = match.group(1)
    
    title = match.group(2)
    
    # 第二行是作者
    author_text = lines[1].strip() if len(lines) > 1 else ""
    
    # 第三行是期刊信息
    other_text = lines[2].strip() if len(lines) > 2 else ""
    
    # 从期刊信息中提取年份(支持中文全角括号（）和英文半角括号())
    year_match = re.search(r'[(\uff08](\d{4})[\)\uff09]', other_text)
    year = year_match.group(1) if year_match else "2015"
    
    # 确定publication_types
    pub_type = "中文" if is_chinese else "English"
    
    return {
        'number': number,
        'title': title,
        'author_text': author_text,
        'other_text': other_text,
        'year': year,
        'publication_type': pub_type
    }

def create_index_md(base_path, entry):
    """
    创建目录和index.md文件
    """
    # 创建目录
    folder_path = os.path.join(base_path, entry['number'])
    os.makedirs(folder_path, exist_ok=True)
    
    # 创建index.md内容
    md_content = f"""---
title: {entry['title']}
author_text: {entry['author_text']}
other_text: {entry['other_text']}

year: "{entry['year']}"
doi: ""
publication_types: ["{entry['publication_type']}"]
---
"""
    
    # 写入index.md文件
    index_path = os.path.join(folder_path, 'index.md')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"已创建: {folder_path}/index.md")

def process_new_txt(file_path):
    """
    处理new.txt文件
    """
    # 读取文件
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 获取基础路径
    base_path = os.path.dirname(file_path)
    
    # 解析每个条目
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # 检查是否是条目的开始(以数字和点开头,或中文数字和冒号开头)
        if re.match(r'^\d+\.', line) or re.match(r'^\s*[一二三四五六七八九十]+：', line):
            # 收集这个条目的所有行(通常是3行)
            entry_lines = []
            entry_lines.append(lines[i])
            
            # 读取后续的作者行和期刊行
            j = i + 1
            while j < len(lines) and j < i + 3:
                next_line = lines[j].strip()
                # 如果遇到下一个条目,停止
                if re.match(r'^\d+\.', next_line) or re.match(r'^\s*[一二三四五六七八九十]+：', next_line):
                    break
                if next_line:  # 只添加非空行
                    entry_lines.append(lines[j])
                j += 1
            
            # 解析条目
            if len(entry_lines) >= 3:
                entry = parse_publication_entry(entry_lines)
                if entry:
                    create_index_md(base_path, entry)
            
            i = j
        else:
            i += 1

if __name__ == "__main__":
    # 获取脚本所在目录的new.txt文件
    script_dir = os.path.dirname(os.path.abspath(__file__))
    txt_file = os.path.join(script_dir, 'new.txt')
    
    if os.path.exists(txt_file):
        print(f"开始处理文件: {txt_file}")
        
        # 先检查文件行数
        with open(txt_file, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
        print(f"文件总行数: {len(all_lines)}")
        print(f"最后一行: {repr(all_lines[-1][:50] if all_lines else 'Empty')}")
        
        process_new_txt(txt_file)
        print("处理完成!")
    else:
        print(f"错误: 找不到文件 {txt_file}")
