import os
import argparse
import pandas as pd
import pdfplumber
from markdownify import markdownify as md_convert
from docx import Document
import yaml
import email
from email import policy

def ensure_mdx_extension(filename):
    base, _ = os.path.splitext(filename)
    return f"{base}.mdx"

def write_mdx(content, output_path, title=None):
    frontmatter = {}
    if title:
        frontmatter['title'] = title

    if frontmatter:
        yaml_frontmatter = yaml.dump(frontmatter, default_flow_style=False)
        full_content = f"---\n{yaml_frontmatter}---\n\n{content}"
    else:
        full_content = content

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(full_content)
    print(f"Successfully converted to {output_path}")

def convert_md_to_mdx(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if it already has frontmatter
    if not content.startswith('---'):
        title = os.path.basename(input_path).split('.')[0].replace('-', ' ').title()
        write_mdx(content, output_path, title=title)
    else:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Successfully converted to {output_path}")

def convert_mdx_to_md(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Successfully converted to {output_path}")

def convert_pdf_to_mdx(input_path, output_path):
    content = ""
    with pdfplumber.open(input_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                content += text + "\n\n"

    title = os.path.basename(input_path).split('.')[0].replace('-', ' ').title()
    write_mdx(content, output_path, title=title)

def convert_html_to_mdx(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    markdown_content = md_convert(html_content)
    title = os.path.basename(input_path).split('.')[0].replace('-', ' ').title()
    write_mdx(markdown_content, output_path, title=title)

def convert_mhtml_to_mdx(input_path, output_path):
    with open(input_path, 'rb') as f:
        msg = email.message_from_binary_file(f, policy=policy.default)

    html_content = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == 'text/html':
                html_content = part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8')
                break
    else:
        if msg.get_content_type() == 'text/html':
            html_content = msg.get_payload(decode=True).decode(msg.get_content_charset() or 'utf-8')

    if not html_content:
        # Fallback to plain text if no HTML part found
        payload = msg.get_payload(decode=True)
        if payload:
            html_content = payload.decode(msg.get_content_charset() or 'utf-8')
        else:
            html_content = ""

    markdown_content = md_convert(html_content)
    title = os.path.basename(input_path).split('.')[0].replace('-', ' ').title()
    write_mdx(markdown_content, output_path, title=title)

def convert_docx_to_mdx(input_path, output_path):
    doc = Document(input_path)
    content = ""
    for para in doc.paragraphs:
        content += para.text + "\n\n"

    title = os.path.basename(input_path).split('.')[0].replace('-', ' ').title()
    write_mdx(content, output_path, title=title)

def convert_csv_to_mdx(input_path, output_path):
    df = pd.read_csv(input_path)
    markdown_table = df.to_markdown(index=False)

    title = os.path.basename(input_path).split('.')[0].replace('-', ' ').title()
    write_mdx(markdown_table, output_path, title=title)

def main():
    parser = argparse.ArgumentParser(description='Convert various formats to MDX')
    parser.add_argument('input', help='Input file path')
    parser.add_argument('--output', help='Output file path')
    parser.add_argument('--format', help='Input format (md, mdx, pdf, html, mhtml, docx, csv)', required=True)

    args = parser.parse_args()

    input_path = args.input
    input_format = args.format.lower()

    if not args.output:
        if input_format == 'mdx':
            output_path = os.path.splitext(input_path)[0] + ".md"
        else:
            output_path = ensure_mdx_extension(input_path)
    else:
        output_path = args.output

    if input_format == 'md':
        convert_md_to_mdx(input_path, output_path)
    elif input_format == 'mdx':
        convert_mdx_to_md(input_path, output_path)
    elif input_format == 'pdf':
        convert_pdf_to_mdx(input_path, output_path)
    elif input_format == 'html':
        convert_html_to_mdx(input_path, output_path)
    elif input_format == 'mhtml':
        convert_mhtml_to_mdx(input_path, output_path)
    elif input_format == 'docx':
        convert_docx_to_mdx(input_path, output_path)
    elif input_format == 'csv':
        convert_csv_to_mdx(input_path, output_path)
    else:
        print(f"Unsupported format: {input_format}")

if __name__ == "__main__":
    main()
